import streamlit as st
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import math 
import time

# ---------- PAGE CONFIGURATION

st.set_page_config(
    page_title='Web of Science Downloader',
    layout='wide')

st.markdown(
    """
    <style>            
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .footer {
        position: fixed;
        display: block;
        width: 100%;
        bottom: 0;
        color: rgba(49, 51, 63, 0.4);
    }
    a:link , a:visited{
        color: rgba(49, 51, 63, 0.4);
        background-color: transparent;
        text-decoration: underline;
    }
    </style>
    <div class="footer">
        <p>
            Developed by 
            <a href="https://github.com/albert-pang" target="_blank">
            Albert (GITM) and Tomy Tjandra (CS) - NTUST
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    url = st.text_input("Enter URL")

    if st.button("Start"):
        options = Options()
        # Get the current directory where the script is located
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Specify the path to the bundled Chrome (115.0.5790.102)
        chrome_path = os.path.join(current_directory, r"Chrome/Application/chrome.exe")
        # Specify the path to the chromedriver (115.0.5790.102)
        chromedriver_path = os.path.join(current_directory, r"Chromedriver/chromedriver.exe")
        options.binary_location = chrome_path
        #driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()

        try:
            # access url
            driver.get(url)
            time.sleep(10)

            # Check if specific elements present for university network front page and other network front page
            university_elements_present = is_university_front_page(driver)
            other_network_elements_present = is_other_network_front_page(driver)

            if university_elements_present:
                download_data_university(driver, url)
            elif other_network_elements_present:
                download_data_other_network(driver, url)
            else:
                st.error("Front page not recognized. Cannot proceed with download.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            driver.quit()

def is_university_front_page(driver):
    try:
        driver.find_element(By.ID, "onetrust-close-btn-container")
        return True
    except:
        return False

def download_data_university(driver, url):
    try:
        # close popup notifications
        onetrust_banner = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "onetrust-close-btn-container"))
        )
        onetrust_banner.click()

        tour_close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Close this tour']"))
        )
        tour_close_button.click()
    except:
        pass

    # get the number of results
    n_result = driver.find_element(By.CLASS_NAME, "brand-blue").text  # get the text
    n_result = int(n_result.replace(",", ""))  # remove comma and change to integer

    # determine number of iterations required
    n_iter = math.ceil(n_result / 500)

    progress_bar = st.progress(0)
    TIME_GAP = 1
    for iter in range(n_iter):
        # progress bar
        progress_text = f"Downloading {iter+1} out of {n_iter} file(s). Please don't close the browser."
        progress_bar.progress(iter/n_iter, text=progress_text)

        # click Export
        time.sleep(TIME_GAP)
        driver.find_element(By.TAG_NAME, "app-export-menu").click()

        # choose Tab Delimited File
        time.sleep(TIME_GAP)
        driver.find_element(By.CSS_SELECTOR, "[aria-label='Tab delimited file']").click()        

        # choose the second radio button
        time.sleep(TIME_GAP)
        driver.find_element(By.CSS_SELECTOR, "[for='radio3-input']").click()

        # input from and to
        time.sleep(TIME_GAP)
        from_rec, to_rec = 500*iter+1, 500*(iter+1)
        input_el_from, input_el_to = driver.find_elements(By.CLASS_NAME, "mat-input-element")
        input_el_from.clear()
        input_el_from.send_keys(from_rec)
        input_el_to.clear()
        input_el_to.send_keys(to_rec)

        # click dropdown
        time.sleep(TIME_GAP)
        driver.find_element(By.CLASS_NAME, "dropdown").click()

        # choose Full Record and Cited References
        time.sleep(TIME_GAP)
        driver.find_element(By.CSS_SELECTOR, "[title='Full Record and Cited References']").click()

        # click Export
        time.sleep(TIME_GAP)
        for btn in driver.find_elements(By.TAG_NAME, 'button'):
            if btn.text == 'Export':
                btn.click()
                break

        # Wait until the popup dialog is not visible
        wait = WebDriverWait(driver, 60)
        while True:
            try:
                wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, "window")))
                break
            except TimeoutException:
                print("Timed out waiting for popup dialog to disappear, retrying...")

        st.success(f"SUCCESS DOWNLOADED FROM {from_rec} TO {to_rec}")

def is_other_network_front_page(driver):
    try:
        driver.find_element(By.ID, "mat-input-0")
        driver.find_element(By.ID, "mat-input-1")
        driver.find_element(By.ID, "signIn-btn")
        return True
    except:
        return False

def download_data_other_network(driver, url):
    try:
        # Wait for the user to click the sign-in button
        sign_in_button = driver.find_element(By.ID, "signIn-btn")
        WebDriverWait(driver, 300).until(EC.invisibility_of_element(sign_in_button))

        # close popup notifications
        onetrust_banner = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "onetrust-close-btn-container"))
        )
        onetrust_banner.click()
        tour_close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='Close this tour']"))
        )
        tour_close_button.click()
    except:
        pass

    # get the number of results
    n_result = driver.find_element(By.CLASS_NAME, "brand-blue").text  # get the text
    n_result = int(n_result.replace(",", ""))  # remove comma and change to integer

    # determine number of iterations required
    n_iter = math.ceil(n_result / 500)

    progress_bar = st.progress(0)
    TIME_GAP = 1
    for iter in range(n_iter):
        # progress bar
        progress_text = f"Downloading {iter+1} out of {n_iter} file(s). Please don't close the browser."
        progress_bar.progress(iter/n_iter, text=progress_text)

        # click Export
        time.sleep(TIME_GAP)
        driver.find_element(By.TAG_NAME, "app-export-menu").click()

        # choose Tab Delimited File
        time.sleep(TIME_GAP)
        driver.find_element(By.CSS_SELECTOR, "[aria-label='Tab delimited file']").click()        

        # choose the second radio button
        time.sleep(TIME_GAP)
        driver.find_element(By.CSS_SELECTOR, "[for='radio3-input']").click()

        # input from and to
        time.sleep(TIME_GAP)
        from_rec, to_rec = 500*iter+1, 500*(iter+1)
        input_el_from, input_el_to = driver.find_elements(By.CLASS_NAME, "mat-input-element")
        input_el_from.clear()
        input_el_from.send_keys(from_rec)
        input_el_to.clear()
        input_el_to.send_keys(to_rec)

        # click dropdown
        time.sleep(TIME_GAP)
        driver.find_element(By.CLASS_NAME, "dropdown").click()

        # choose Full Record and Cited References
        time.sleep(TIME_GAP)
        driver.find_element(By.CSS_SELECTOR, "[title='Full Record and Cited References']").click()

        # click Export
        time.sleep(TIME_GAP)
        for btn in driver.find_elements(By.TAG_NAME, 'button'):
            if btn.text == 'Export':
                btn.click()
                break

        # Wait until the popup dialog is not visible
        wait = WebDriverWait(driver, 60)
        while True:
            try:
                wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, "window")))
                break
            except TimeoutException:
                print("Timed out waiting for popup dialog to disappear, retrying...")

        st.success(f"SUCCESS DOWNLOADED FROM {from_rec} TO {to_rec}")



if __name__ == "__main__":
    main()
