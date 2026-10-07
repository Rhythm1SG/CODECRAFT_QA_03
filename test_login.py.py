"""
Automated login tests (Playwright + pytest)
Target: https://the-internet.herokuapp.com/login  (public demo site)
Valid credentials on this site: tomsmith / SuperSecretPassword!
"""
import pytest
from playwright.sync_api import Page, expect

LOGIN_URL = "https://the-internet.herokuapp.com/login"
VALID_USER = "tomsmith"
VALID_PASS = "SuperSecretPassword!"
WAIT = 30000  # ms - the demo site can be slow, so be patient


# ---------- Page Object ----------
class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.locator("#username")
        self.password = page.locator("#password")
        self.submit = page.locator("button[type='submit']")
        self.flash = page.locator("#flash")

    def open(self):
        self.page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

    def login(self, user: str, pwd: str):
        self.username.fill(user)
        self.password.fill(pwd)
        self.submit.click()
        self.page.wait_for_load_state("domcontentloaded")


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    return lp


# ---------- Positive tests ----------
def test_valid_login(login_page: LoginPage, page: Page):
    login_page.login(VALID_USER, VALID_PASS)
    expect(page).to_have_url("https://the-internet.herokuapp.com/secure", timeout=WAIT)
    expect(login_page.flash).to_contain_text("You logged into a secure area!", timeout=WAIT)


def test_logout_after_login(login_page: LoginPage, page: Page):
    login_page.login(VALID_USER, VALID_PASS)
    page.get_by_role("link", name="Logout").click()
    expect(page).to_have_url(LOGIN_URL, timeout=WAIT)
    expect(login_page.flash).to_contain_text("You logged out of the secure area!", timeout=WAIT)


# ---------- Negative tests ----------
@pytest.mark.parametrize(
    "user, pwd, expected_error",
    [
        ("wronguser", VALID_PASS, "Your username is invalid!"),       # invalid username
        (VALID_USER, "wrongpass", "Your password is invalid!"),       # invalid password
        ("wronguser", "wrongpass", "Your username is invalid!"),      # both invalid
        ("", "", "Your username is invalid!"),                        # both empty
        ("", VALID_PASS, "Your username is invalid!"),                # empty username
        (VALID_USER, "", "Your password is invalid!"),                # empty password
    ],
    ids=[
        "invalid_username",
        "invalid_password",
        "both_invalid",
        "both_empty",
        "empty_username",
        "empty_password",
    ],
)
def test_invalid_login(login_page: LoginPage, page: Page, user, pwd, expected_error):
    login_page.login(user, pwd)
    expect(login_page.flash).to_contain_text(expected_error, timeout=WAIT)
    expect(page).to_have_url(LOGIN_URL, timeout=WAIT)  # stays on login page
