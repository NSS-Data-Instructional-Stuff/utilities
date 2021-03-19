
from __future__ import annotations

from collections import namedtuple
import logging
import re

import numpy as np
import pandas as pd

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NoSuchAssignmentException(Exception):
    pass


Secrets = namedtuple('Secrets', ['email', 'password'])


def must_be_logged_in(f):
    def inner(f_self: DataCamp, *args, **kwargs):
        if not f_self.logged_in:
            f_self.login()

        return f(f_self, *args, **kwargs)
    return inner


def must_have_org(f):
    def inner(f_self: DataCamp, *args, **kwargs):
        if f_self.org_name is None:
            f_self.reset_org_name()

        return f(f_self, *args, **kwargs)
    return inner


class DataCamp:

    BASE_URL = 'https://www.datacamp.com'

    def __init__(self, driver: Chrome, secrets: Secrets, org_name=None):
        self.org_name = org_name

        self._driver = driver
        self._secrets = secrets
        self._logged_in = False

    @property
    def logged_in(self):
        return self._logged_in

    def reset_org_name(self):
        self.org_name = self.get_org_name()

    def get_org_name(self):
        self.goto('/enterprise')

        organizations = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "organizations"))
        ).find_elements_by_xpath('//li[contains(@class, "organization")]//a')

        org_attributes = []
        org_ptrn = re.compile(r'enterprise/(?P<org_name>.*?)(?:/|$)')
        for org_web_elem in organizations:
            href = org_ptrn.search(org_web_elem.get_attribute('href'))
            if not href:
                continue

            href = href.group('org_name')
            title = org_web_elem.find_element_by_tag_name('h4').text
            org_attributes.append((href, title))

        def select_org_from_list(orgs):
            selections = ''.join([f'\t{str(ind+1)}. {title}\n' for ind, (_, title) in enumerate(orgs)])
            result = input(f'Select which org you would like to focus on:\n{selections}')

            try:
                assert int(result) in range(1, len(orgs)+1)

            except (AssertionError, ValueError):
                logger.warning(f'Answer must be an integer (1-{len(orgs)}). Please try again.')
                return select_org_from_list(orgs)

            else:
                return orgs[int(result)-1]

        href, title = select_org_from_list(org_attributes)
        return href

    def goto(self, page, wait=2):
        url = f'{self.BASE_URL}{page}'
        logger.info(f'Going to url: {url}')

        self._driver.get(url)
        self._driver.implicitly_wait(wait)

    def login(self):
        logger.info('Logging in.')
        self._driver.get('https://www.datacamp.com/users/sign_in')

        form = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.ID, "new_user"))
        )

        email_input = WebDriverWait(form, 10).until(
            EC.presence_of_element_located((By.ID, "user_email"))
        )
        email_input.send_keys(self._secrets.email)
        self._driver.implicitly_wait(2)

        next_button = WebDriverWait(form, 10).until(
            EC.element_to_be_clickable((By.TAG_NAME, "button"))
        )
        next_button.click()
        self._driver.implicitly_wait(2)

        password_input = WebDriverWait(form, 10).until(
            EC.presence_of_element_located((By.ID, "user_password"))
        )
        password_input.send_keys(self._secrets.password)
        self._driver.implicitly_wait(2)

        signin_button = WebDriverWait(form, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        signin_button.click()

        WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "groups"))
        )

        self._logged_in = True
        logger.info('Successfully logged in.')

    @must_be_logged_in
    @must_have_org
    def get_org_summary_df(self) -> pd.DataFrame:
        logger.info('Getting assignments summary dataframe.')
        self._goto_assignments()

        df = self._get_table_component_df()

        df.columns = ['assignment_name', 'assigned_to', 'assigned_date',
                      'due_date', 'type', 'num_completed', 'num_late', 'num_missed', '?']
        df.loc[:, 'assigned_date'] = pd.to_datetime(df['assigned_date'], format='%b %d, %Y')
        df.loc[:, 'due_date'] = df.loc[:, 'due_date'].str.replace(r'\s\w+$', '')
        df.loc[:, 'due_date'] = pd.to_datetime(df['due_date'], format='%b %d, %Y, %H:%M')
        df.loc[:, 'assignment_name_len'] = df['assignment_name'].apply(lambda x: len(x))

        df = df[
            ['assignment_name', 'assigned_date', 'due_date', 'num_completed', 'num_late', 'num_missed']] \
            .sort_values('due_date', ascending=False)

        return df

    @must_be_logged_in
    @must_have_org
    def get_assignment_summary_df_by_name(self, assignment_name):

        self._goto_assignments()

        try:
            assignment = self._driver.find_element_by_xpath(f'//td[text()="{assignment_name}"]')

        except NoSuchElementException as e:
            raise NoSuchAssignmentException(f'Assignment {assignment_name} not found.. TB: {e.msg}')

        else:
            logger.info(f'Assignment {assignment_name} found on summary page, getting summary dataframe.')
            assignment.click()
            self._driver.implicitly_wait(2)

            # title
            xpath = f'//*[@id="content"]//h2[contains(text(), "{assignment_name}")]'
            logger.info(f'Waiting for {xpath}')
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            df = self._get_table_component_df()

            df.columns = ['email', 'student_name', 'status', 'date_completed']

            df.loc[:, 'email'] = df['email'].str.replace(r'[A-Z]\s', '')
            df.loc[:, 'date_completed'] = df['date_completed'].replace('Not yet completed', np.NaN)
            # removing tz info
            df.loc[:, 'date_completed'] = df['date_completed'].str.replace(r'\s[A-Z]+$', '')
            df.loc[:, 'date_completed'] = pd.to_datetime(df['date_completed'], format='%b %d, %Y, %H:%M')

            return df

    @must_be_logged_in
    @must_have_org
    def get_student_assignment_report(self):
        self.goto(f'/enterprise/{self.org_name}/reporting')

        # title
        WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//h2[contains(text(), "Reporting")]'))
        )

        df = self._get_table_component_df()
        df.columns = ['email', 'name', 'courses_completed', 'exercises_completed', 'chapters_completed', 'xp']

        return df

    def quit(self):
        self._driver.close()
        self._logged_in = False

    def _get_table_component_df(self):
        logger.info('Getting table component.')
        table_parent = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-component"))
        )

        dfs = pd.read_html(table_parent.get_attribute('innerHTML'))

        if len(dfs) > 1:
            logger.warning(f'More than one table returned, just returning the first one.')

        return dfs[0]

    def _goto_assignments(self):
        self.goto(f'/enterprise/{self.org_name}/assignments')
        WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content"]//h2[contains(text(), "Assignments")]'))
        )


if __name__ == '__main__':
    import secrets

    driver = Chrome()
    dc_driver = DataCamp(
        driver,
        secrets=Secrets(secrets.email, secrets.password)
    )

    assignments_summary_df = dc_driver.get_org_summary_df()
    print(assignments_summary_df.head())
