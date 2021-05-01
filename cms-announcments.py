#!/usr/bin/env python3
import argparse
import sys
from signal import SIGINT, signal
import requests
import urllib3
from rich import print as r_print
from rich.console import Console
from bs4 import BeautifulSoup as bs
import getpass
HOST = 'https://cms.guc.edu.eg'
import re
from requests_ntlm import HttpNtlmAuth
console = Console()
COURSE_REGEX ="\n*[\(][\|]([^\|]*)[\|][\)]([^\(]*)[\(].*\n*"
COURSE_REPALCE='[\\1]\\2'
def get_announcements(course_page_soup):
    """get course announcements"""
    announcements = course_page_soup.find('div', class_='row').find_all('p')
    return [announcement.text for announcement in announcements]

def get_course_soup(course_url, username, password, session):
    """get course html for given course"""
    course_page = session.get(course_url, verify=False,
                              auth=HttpNtlmAuth(username, password))
    return bs(course_page.text, 'html.parser')

def print_announcement(course, username, password, course_url, session):
    '''print the announcement'''
    announcements = get_announcements(get_course_soup(
        course_url, username, password, session))
    console = Console()
    if len(announcements) == 0:
        return
    console.print(f'[bold][red]{course}[/red][/bold]', justify='center')
    print()
    for item in announcements:
        if item == '':
            continue
        console.print(item.strip(), justify='center')
    print()


def authenticate_user(username, password):
    """validate user credentials."""
    session = requests.Session()
    request_session = session.get(HOST,
                                  verify=False, auth=HttpNtlmAuth(username, password))
    return request_session.status_code == 200


def get_cardinalities():
    """login to cms website."""
    try:
        with open(".env", "r") as file_env:
            lines = file_env.readlines()
            cred = (lines[0].strip(), lines[1].strip())
    except FileNotFoundError:
        cred = (input("Enter Your GUC username :  "),
                getpass.getpass(prompt="Enter Your GUC Password : "))
        with open(".env", "w") as file_env:
            file_env.write(f"{cred[0]}\n{cred[1]}")
    return cred


def get_links(links_tags):
    """remove null objects."""
    return [link.get('href') for link in links_tags if link.get('href') is not None]


def get_avaliable_courses(home_page_soup):
    """fetch courses links"""
    link_tags = get_links(home_page_soup('a'))
    return [
        HOST + course_link
        for course_link in link_tags
        if re.match(r'\/apps\/student\/CourseViewStn\?id(.*)', course_link)
    ]


def get_course_names(home_page_soup):
    """get courses names"""
    courses_table = list(home_page_soup.find('table', {
        'id': 'ContentPlaceHolderright_ContentPlaceHoldercontent_GridViewcourses'}))
    return [
        re.sub(
            COURSE_REGEX,
            COURSE_REPALCE,
            courses_table[i].text.strip(),
        )
        for i in range(2, len(courses_table) - 1)
    ]



if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    username, password = get_cardinalities()
    if authenticate_user(username, password):
        console.rule("[+] Authorized", style='bold green')
    else:
        console.rule(
            "[!] you are not authorized. review your credentials", style='bold red')
        os.remove(".env")
        sys.exit(1)

    session = requests.Session()
    home_page = session.get(HOST,
                            verify=False, auth=HttpNtlmAuth(username, password))
    home_page_soup = bs(home_page.text, 'html.parser')

    course_links = get_avaliable_courses(home_page_soup)
    courses_name = get_course_names(home_page_soup)
    
    for index, course_url in enumerate(course_links):
            print_announcement(
                courses_name[index], username, password, course_url, session)
    sys.exit(0)
