import requests
from bs4 import BeautifulSoup

# This is your test result code to check for
userCode = "123456789"  # digits

# Header to handle any compressions
headers = {'Accept-Encoding': 'identity'}
response = requests.get(
    'https://provsvar1177.regionkronoberg.se/corona', headers=headers)

# Extract cookie to be sent with POST request
cookieName = ""
cookieValue = ""
for cookie in response.cookies:
    if ("antiforg" in cookie.name.lower()):
        cookieName = cookie.name
        cookieValue = cookie.value

# Extract requestVerificationToken to be sent as body in POST request.
# Get t value in the hidden input field with name attribute "__RequestVerificationToken"
requestVerificationToken = BeautifulSoup(response.content, features="html.parser").findAll(
    attrs={'name': '__RequestVerificationToken'})
token = requestVerificationToken[0]["value"]

# ************************************************************
# Post request to server need to have the following headers
# Url = provsvar1177.regionkronoberg.se/corona/GetResultByCode
# ************************************************************
# Accept: application/json, text/javascript, */*; q=0.01
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# Cookie: .AspNetCore.Antiforgery.XXXXX=YYYYYYYYYYYYY
# Body: __RequestVerificationToken=ZZZZZZZZZ&userCode=101631103

headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
           'Content-Type': 'application/x-www-form-urlencoded; charset = UTF-8',
           'Cookie': cookieName + '=' + cookieValue}
body = '__RequestVerificationToken=' + token + '&userCode=' + userCode
response = requests.post(
    'https://provsvar1177.regionkronoberg.se/corona/GetResultByCode', headers=headers, data=body)

if "RESULTAT HITTAS EJ".lower() in response.text.lower():
    print("Resultatet ej färdigt")
else:
    # Result exist, send email or SMS
    print(response.text)
