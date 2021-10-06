*** Settings ***
Library SeleniumLibrary

*** Test Cases ***
Search On Google
     Open Browser    http://www.google.com    Chrome
     Wait Until Page Contains Element    cnsw
     Select Frame    //iframe
     Submit Form    //form
     Input Text    name=q    Stephen\ Hawking
     Press Keys    name=q    ENTER
     Page Should Contain    Wikipedia
     Close Window