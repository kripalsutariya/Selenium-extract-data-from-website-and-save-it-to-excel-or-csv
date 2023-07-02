
"""
This script will extract data from 'https://dash.sparkloop.app/partner_profile/upscribe/visual_editor?open_paid_recommendations=true'
"""

import time

import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

website_url = "https://dash.sparkloop.app/partner_profile/upscribe/visual_editor?open_paid_recommendations=true"
path_of_excel_file_containing_username_and_password = ""

df = pd.read_excel(
    rf"{path_of_excel_file_containing_username_and_password}.xlsx")


def create_firefox_options():
    """
    This function creates required instances to run firefox browser.
    """

    firefox_options = Options()
    firefox_options.add_argument("-headless")
    firefox_options.set_preference(
        "browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("broeser.helperApps.alwaysAsk.force", False)

    return Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)


def open_webpage(driver, url):
    """
    This function opens webpage in firefox browser.

    Args:
        driver (_type_): driver created for firefox browser
        url (_type_): url of webpage(str)
    """

    return driver.get(url)


def login(driver, acc_username, acc_password):
    """
    This function is created to log into website at https://dash.sparkloop.app/login

    Args:
    - driver: driver created for firefox browser
    - acc_username: username of the account(str)
    - acc_password: password of the account(str)
    """

    username = driver.find_element(By.XPATH, "//input[@id='user_email']")
    username.clear()
    username.send_keys(acc_username)

    password = driver.find_element(By.XPATH, "//input[@id='user_password']")
    password.clear()
    password.send_keys(acc_password)

    return driver.find_element(By.XPATH, "//input[@value='Log in']").click()


def get_data(driver, total_pages):
    """
    This function extracts data from sparkloop website

    Args:
    - driver: driver created for firefox browser
    - total_pages: total number of pages from which data is going to be extracted

    Returns:
        l_data: List of the data in  the form of dictionaries
    """

    l_data = []

    for page_num in range(total_pages):
        print('Getting data from page:', page_num+1, '\n')

        data_elements = driver.find_element(
            By.XPATH, "//div[@class='divide-y space-y-3']").find_elements(By.XPATH, "//div[@data-controller='toggle']")[1:]

        for data_element in data_elements:

            name = ''
            payout = ''
            max_payout = ''
            geographic_restrictions = ''
            terms_and_conditions = ''
            pending_duration = ''
            publication_language = ''
            budget_usage = ''

            try:
                data_element.find_element(
                    By.CLASS_NAME, 'btn.btn--outlined').click()
            except:
                time.sleep(2)
                data_element.find_element(
                    By.CLASS_NAME, 'btn.btn--outlined').click()

            time.sleep(2)

            info_soup = data_element.find_elements(By.TAG_NAME, 'dt')

            for info in info_soup:
                try:
                    name = data_element.find_element(
                        By.CSS_SELECTOR, 'h3.text-lg.font-semibold.flex.space-x-2.items-center').text.strip()
                except:
                    pass

                if info.text.strip() == 'Payout':
                    payout = info.find_element(
                        By.XPATH, "following-sibling::*[1]").text

                    if '/' in payout:
                        payout = payout.split('/')[0].replace('$', '').strip()
                    if '.00' in payout:
                        payout = int(float(payout))

                if info.text.strip() == 'Max. payout':
                    max_payout = info.find_element(
                        By.XPATH, "following-sibling::*[1]").text

                    if '/' in max_payout:
                        max_payout = max_payout.split(
                            '/')[0].replace('$', '').strip()
                    if '.00' in max_payout:
                        max_payout = int(float(max_payout))

                if info.text.strip() == 'Geographic restrictions':
                    geographic_elem = info.find_element(
                        By.XPATH, "following-sibling::*[1]")

                    l_geographic_restrictions = []

                    for restriction in geographic_elem.find_elements(By.CSS_SELECTOR, 'div.inline-block.mb-2'):
                        l_geographic_restrictions.append(restriction.text)

                    geographic_restrictions = ', '.join(
                        l_geographic_restrictions)

                if info.text.strip() == 'Terms & Conditions':
                    terms_and_conditions = info.find_element(
                        By.XPATH, "following-sibling::*[1]").text

                if info.text.strip() == 'Referral pending duration':
                    pending_duration = info.find_element(
                        By.XPATH, "following-sibling::*[1]").text.split(' ')[0].strip()

                if info.text.strip() == 'Publication language':
                    publication_language = info.find_element(
                        By.XPATH, "following-sibling::*[1]").text

                try:
                    budget_usage = data_element.find_element(
                        By.CSS_SELECTOR, 'i.uil.uil-exclamation-triangle').find_element(By.XPATH, "following-sibling::*[1]").text
                except:
                    pass

            data = {
                'Name': name,
                'Payout': payout,
                'Maximum Payout': max_payout,
                'Budget Usage': budget_usage,
                'Geographical Restriction': geographic_restrictions,
                'Referral Pending Duration': pending_duration,
                'Terms & Conditions': terms_and_conditions,
                'Publication Language': publication_language
            }

            l_data.append(data)

        if page_num+1 == 24:
            continue
        driver.find_element(By.XPATH, "//a[@class='pagination-next']").click()
        time.sleep(3)

    print('Returning data')
    return l_data


def main():
    """
    This function is main part of the script which runs all functions created in this script.
    """

    print('Creating firefox driver', '\n')
    driver = create_firefox_options()
    driver.maximize_window()

    wait = WebDriverWait(driver, 360)

    for index, row in df.iterrows():
        print('Getting username and password for account:', index+1, '\n')
        acc_username = row['Username']
        acc_password = row['Password']

        print('Opening webpage.', '\n')
        open_webpage(driver, website_url)

        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@value='Log in']")))

        print('Logging in.', '\n')
        login(driver, acc_username, acc_password)
        wait.until(lambda driver: driver.current_url ==
                   "https://dash.sparkloop.app/partner_profile/upscribe/visual_editor?open_paid_recommendations=true")
        time.sleep(1)

        total_pages = int(driver.find_element(
            By.XPATH, "//div[@role='navigation']").find_elements(By.XPATH, "//li")[-2].text.strip())
        print('Total pages for this account:', total_pages, '\n')

        data_list = get_data(driver, total_pages)

        print('Saving data')
        data_df = pd.DataFrame(data_list)
        data_df.to_csv(f'sparkloop data {acc_username}.csv', index=False)

    print('Closing Window.')
    print('DATA FILe CREATED SUCCESSFULLY!!!!!!')


if __name__ == "__main__":
    main()
