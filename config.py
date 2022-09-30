import os


class Config(object):
    # In a production app, store this instead in KeyVault or an environment variable

    CLIENT_SECRET = os.environ.get("AZURE_APP_SECRET", "AZURE_APP_SECRET")

    AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
    # AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

    CLIENT_ID = os.environ.get("CLIENT_ID", "CLIENT_ID")

    #   Note that this will be the end of the URI entered back in Azure AD
    REDIRECT_PATH = "/" + os.environ.get(
        "REDIRECT_PATH", "REDIRECT_PATH"
    )  # Used to form an absolute URL,
    # which must match your app's redirect_uri set in AAD

    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    SCOPE = ["User.Read"]

    SESSION_TYPE = "filesystem"  # So token cache will be stored in server-side session
