"""
Create Directed NetworkX Structural Graph

Create a directed NetworkX graph from a dictionary of lists adjacency representation,
where each key is the source page, and the value is a list of pages the source page
hyperlinks to.

Returns:
  A directed NetworkX graph `G_structural`
"""

# Import modules
import networkx as nx

# Set up data
page_links_proc = {
    "https://signin.account.gov.uk/sign-in-or-create": [
        "https://signin.account.gov.uk/enter-email-create",
        "https://signin.account.gov.uk/enter-email",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/enter-email": [
        "https://signin.account.gov.uk/enter-password",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/enter-password": [
        "https://signin.account.gov.uk/reset-password-check-email",
        "https://www.gov.uk/email/subscriptions/account/confirm",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://www.gov.uk/email/subscriptions/account/confirm": [
        "https://www.gov.uk",
        "https://www.gov.uk/guidance/move-to-the-uk-if-youre-from-ukraine",
    ],
    "https://www.gov.uk/guidance/move-to-the-uk-if-youre-from-ukraine": [
        "https://www.gov.uk/email/manage"
    ],
    "https://signin.account.gov.uk/reset-password-check-email": [
        "https://signin.account.gov.uk/reset-password",
        "https://signin.account.gov.uk/reset-password-resend-code",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/reset-password-resend-code": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/enter-password-account-exists",
        "https://signin.account.gov.uk/reset-password-check-email",
    ],
    "https://signin.account.gov.uk/reset-password": [
        "https://signin.account.gov.uk/enter-code",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/enter-code": [
        "https://signin.account.gov.uk/contact-us",
        "https://account.gov.uk/manage-your-account",
        "https://signin.account.gov.uk/resend-code",
    ],
    "https://signin.account.gov.uk/resend-code": [
        "https://signin.account.gov.uk/enter-code",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/enter-email-create": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/check-your-email",
        "https://signin.account.gov.uk/enter-password-account-exists",
    ],
    "https://signin.account.gov.uk/enter-password-account-exists": [
        "https://signin.account.gov.uk/reset-password-check-email",
        "https://signin.account.gov.uk/enter-code",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/check-your-email": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/create-password",
        "https://signin.account.gov.uk/enter-email-create",
    ],
    "https://signin.account.gov.uk/create-password": [
        "https://signin.account.gov.uk/privacy-notice",
        "https://signin.account.gov.uk/terms-and-conditions",
        "https://signin.account.gov.uk/enter-phone-number",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/enter-phone-number": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/check-your-phone",
    ],
    "https://signin.account.gov.uk/check-your-phone": [
        "https://signin.account.gov.uk/enter-phone-number",
        "https://signin.account.gov.uk/account-created",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/account-created": [
        "https://signin.account.gov.uk/contact-us",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/email/subscriptions/account/confirm",
    ],
    "https://account.gov.uk/manage-your-account": [
        "https://account.gov.uk/enter-password",
        "https://account.gov.uk/enter-password",
        "https://account.gov.uk/enter-password",
        "https://account.gov.uk/enter-password",
        "https://www.gov.uk/account/home",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://www.gov.uk/account/home": [
        "https://signin.account.gov.uk/contact-us",
        "https://www.gov.uk/sign-in",
        "https://signin.account.gov.uk/signed-out",
        "https://www.gov.uk/email/manage",
        "https://account.gov.uk/manage-your-account",
    ],
    "https://account.gov.uk/enter-password": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/manage-your-account",
        "https://account.gov.uk/change-email",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/enter-password": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/manage-your-account",
        "https://account.gov.uk/change-password",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/change-password": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/signed-out",
        "https://account.gov.uk/password-updated-confirmation",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/account/home",
    ],
    "https://account.gov.uk/password-updated-confirmation": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/manage-your-account",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/change-email": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/signed-out",
        "https://account.gov.uk/check-your-email",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/account/home",
    ],
    "https://account.gov.uk/check-your-email": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/change-email",
        "https://account.gov.uk/email-updated-confirmation",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/email-updated-confirmation": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/signed-out",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/account/home",
    ],
    "https://account.gov.uk/enter-password": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/manage-your-account",
        "https://account.gov.uk/change-phone-number",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/change-phone-number": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/signed-out",
        "https://account.gov.uk/check-your-phone",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/account/home",
    ],
    "https://account.gov.uk/check-your-phone": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/change-phone-number",
        "https://account.gov.uk/phone-number-updated-confirmation",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/phone-number-updated-confirmation": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/signed-out",
        "https://account.gov.uk/manage-your-account",
    ],
    "https://www.gov.uk/email/manage": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/email/manage/unsubscribe-all",
        "https://www.gov.uk/email/unsubscribe/",
        "https://www.gov.uk/email/manage/frequency/",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://www.gov.uk/email/unsubscribe/": ["https://www.gov.uk/email/manage"],
    "https://www.gov.uk/email/manage/unsubscribe-all": [
        "https://www.gov.uk/account/home",
        "https://www.gov.uk/email/manage",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://account.gov.uk/enter-password": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/signed-out",
        "https://account.gov.uk/delete-account",
        "https://account.gov.uk/manage-your-account",
        "https://www.gov.uk/account/home",
    ],
    "https://account.gov.uk/delete-account": [
        "https://www.gov.uk/account/home",
        "https://account.gov.uk/manage-your-account",
        "https://signin.account.gov.uk/signed-out",
        "https://signin.account.gov.uk/contact-us",
        "https://account.gov.uk/account-deleted-confirmation",
    ],
    "https://www.gov.uk/sign-in": [
        "https://www.gov.uk/",
        "https://www.gov.uk/sign-in-childcare-account",
        "https://www.gov.uk/check-state-pension",
        "https://www.gov.uk/report-covid19-result",
        "https://www.gov.uk/log-in-register-hmrc-online-services",
        "https://www.gov.uk/sign-in-universal-credit",
        "https://www.gov.uk/email/manage",
    ],
    "https://signin.account.gov.uk/contact-us": [
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/contact-us-further-information",
    ],
    "https://signin.account.gov.uk/contact-us-further-information": [
        "https://signin.account.gov.uk/contact-us-questions",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/contact-us-questions": [
        "https://signin.account.gov.uk/contact-us-submit-success",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/contact-us-submit-success": [
        "https://www.gov.uk/",
        "https://signin.account.gov.uk/contact-us",
    ],
    "https://signin.account.gov.uk/signed-out": [
        "https://www.gov.uk/",
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/sign-in-or-create",
    ],
    "https://www.gov.uk/email/manage/frequency/": [
        "https://www.gov.uk/account/home",
        "https://www.gov.uk/email/manage",
        "https://signin.account.gov.uk/contact-us",
        "https://signin.account.gov.uk/contact-us-questions",
    ],
    "https://www.gov.uk/email/subscriptions/single-page/new": [
        "https://www.gov.uk/sign-in",
        "https://signin.account.gov.uk/sign-in-or-create",
    ],
}

# Create NetworkX graph
G_structural = nx.from_dict_of_lists(page_links_proc, create_using=nx.DiGraph)

# Explore graph
nx.info(G_structural)
nx.draw(G_structural, with_labels=False)
G_structural.nodes(data=True)
G_structural.edges(data=True)

# Save graph
nx.write_gpickle(G_structural, "../data/processed/G_structural.gpickle")
