import asyncio
import nodriver

def get_time():
    import time
    return time.perf_counter()


async def starting_server(starting):
    start = get_time()
    
    # Create the browser instance
    browser = await nodriver.Browser.create()

    try:
        # Open the target page
        tab = await browser.get("https://aternos.org/go")
        
        # Log in
        input_username = await tab.select("input[placeholder='Username']")
        await input_username.send_keys("StarterBot")
        
        input_password = await tab.select("input[placeholder='••••••••']")
        await input_password.send_keys("BotAccount")
        
        login_button = await tab.select("button[title='Login']")
        await login_button.click()

        # Handle cookies consent if present
        try:
            cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=10)
            await cookies.click()
        except:
            pass

        # Select the server
        server_select = await tab.select('div[title="roadblocksjailbrokey"]', timeout=10)
        await server_select.click()

        # Wait for the server page to load
        await browser.sleep(100000)

    finally:
        await browser.stop()

    end = get_time()
    return end - start


async def get_player_names():
    browser = await nodriver.Browser.create()
    tab = await browser.get("https://aternos.org/go")
    input_username = await tab.select("input[placeholder='Username']")
    await input_username.send_keys("StarterBot")
    input_password = await tab.select("input[placeholder='••••••••']")
    await input_password.send_keys("BotAccount")
    login_button = await tab.select("button[title='Login']")
    await login_button.click()
    cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=100)
    await cookies.click()

    server_select = await tab.select('div[title="roadblocksjailbrokey"]', timeout=10000)
    await server_select.click()  # Wait for login to complete

    # Navigate to players page
    players_link = await tab.select("a[title='Players']")
    await players_link.click()

    # Wait for players list to appear
    player_list_div = await tab.wait_for(".playercardlist.online.collapsed", timeout=20000)
    player_cards = await player_list_div.query_selector_all(".playercard.has-details")

    player_names = []
    for card in player_cards:
        attributes = card.attrs
        player_name = attributes['data-playername']
        player_names.append(player_name)
    await tab.close()
    print(player_names)

    return player_names

if __name__ == '__main__':
    # nodriver.loop().run_until_complete(get_player_names())
    nodriver.loop().run_until_complete(starting_server(False))
