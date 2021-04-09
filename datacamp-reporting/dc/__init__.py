
from enum import Enum
import getpass
import logging
import os
from pathlib import Path

import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from dc.selenium_utils import Secrets, DataCamp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Actions(Enum):
    reset_org = 'Reset Org'
    org_summary = 'Org Summary'
    assignment_summary = 'Assignment Summary'


def _get_email():
    email = os.environ.get('DATACAMP_EMAIL', None)
    if email is None:
        email = input('DC Email:')
        logger.info('If you set "DATACAMP_EMAIL" env variable, I won\'t ask you again!!')

    return email


def _get_password():
    return getpass.getpass(prompt='DC password (hidden):', stream=None)


def download_reports(org_name: str, *, out_dir: Path = None, show: bool = False):
    secrets = Secrets(_get_email(), _get_password())
    options = Options()
    if not show:
        options.add_argument("--headless")

    driver = Chrome(options=options)
    dc_driver = DataCamp(
        driver,
        secrets=Secrets(secrets.email, secrets.password),
        org_name=org_name
    )

    try:

        logger.info('Getting org summary.')
        org_summary_df = dc_driver.get_org_summary_df()

        assignments = []

        logger.info('Getting assignment summary.')
        for assignment in org_summary_df.assignment_name:
            assignment_df = dc_driver.get_assignment_summary_df_by_name(assignment)
            assignment_df['assignment'] = assignment
            assignments.append(assignment_df)

        assignments_df = pd.concat(assignments)

        logger.info('Getting student report summary.')
        student_report_df = dc_driver.get_student_assignment_report()

        org_summary_df.to_csv(out_dir / 'org_summary.csv', index=False)
        assignments_df.to_csv(out_dir / 'assignments.csv', index=False)
        student_report_df.to_csv(out_dir / 'student_report.csv', index=False)

    finally:
        logger.info('Shuttin\' er dayown!')
        dc_driver.quit()
