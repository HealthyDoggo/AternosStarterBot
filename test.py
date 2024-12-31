import asyncio
import nodriver
from bs4 import BeautifulSoup
import re
from helpers import load_correct_ip_addresses, save_correct_ip_addresses, save_pending_responses, save_last_checked_log, load_last_checked_log
from ip2geotools.databases.noncommercial import HostIP
from pyvirtualdisplay import Display

player_ip_addresses = load_correct_ip_addresses()
last_checked_log = load_last_checked_log()

server_queue = asyncio.Queue()
player_queue = asyncio.Queue()

def get_time():
    import time
    return time.perf_counter()
def add_ip_address(username, ip):
    for user in list(player_ip_addresses.keys()):
        if user.lower() == username.lower():
            player_ip_addresses[user].append(ip)
    save_correct_ip_addresses(player_ip_addresses)
def get_correct_ips():
    return player_ip_addresses
async def starting_server(starting):
    if starting:
        return await start_server()
    else:
        return await check_server_status()

async def maintain_players_tab():
    with Display():
        config = nodriver.Config(browser_executable_path="chromium-mac/Chromium.app/Contents/MacOS/Chromium")
        browser = await nodriver.Browser.create(config=config)
        print("Starting player monitoring tab")
        try:
            # Open the target page
            tab = await browser.get("https://aternos.org/go")
            
            # Log in
            try:
                input_username = await tab.select("input[placeholder='Username']")
                await input_username.send_keys("StarterBot")
                
                input_password = await tab.select("input[placeholder='••••••••']")
                await input_password.send_keys("BotAccount")
                
                login_button = await tab.select("button[title='Login']")
                await login_button.click()
            except:
                pass

            # Handle cookies consent if present
            try:
                cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=10)
                await cookies.click()
            except:
                pass

            # Select the server
            server_select = await tab.select('div[title="roadblocksjailbrokey"]', timeout=1000)
            await server_select.click()
            await asyncio.sleep(1.5)

            # Navigate to players page
            players_link = await tab.select("a[title='Players']")
            await players_link.click()
            print("okay made it to the players while true")
            while True:
                try:
                    command = await player_queue.get()
                    if command["action"] == "get_players":
                        try:
                            # Wait for players list to appear
                            player_list_div = await tab.select(".playercardlist.online.collapsed")
                            player_list_div = await tab.wait_for(".playercardlist.online.collapsed", timeout=20000)
                            player_cards = await player_list_div.query_selector_all(".playercard.has-details")

                            player_names = []
                            for card in player_cards:
                                attributes = card.attrs
                                player_name = attributes['data-playername']
                                player_names.append(player_name)
                            
                            await command["response_queue"].put({"players": player_names})
                        except Exception as e:
                            print(f"Error getting player names: {e}")
                            await command["response_queue"].put({"players": []})
                    await asyncio.sleep(0.75)

                except KeyboardInterrupt:
                    print("Code keyboard interrupted.")
                    break

                except Exception as e:
                    print(f"Error in players tab: {e}")
                    await asyncio.sleep(1)

        finally:
            try:
                if tab:
                    await tab.close()
                if browser.connection:
                    await browser.connection.aclose()
                browser.stop()
            except Exception as e:
                print(f"Error during browser closure: {e}")
            finally:
                if browser._process:
                    browser._process.terminate()
                    await browser._process.wait()

async def get_player_names():
    response_queue = asyncio.Queue()
    await player_queue.put({"action": "get_players", "response_queue": response_queue})
    result = await response_queue.get()
    return result["players"]

async def get_logs(client, pending_responses, linked_accounts, console_queue):
    with Display():
        config = nodriver.Config(browser_executable_path="chromium-mac/Chromium.app/Contents/MacOS/Chromium")
        browser = await nodriver.Browser.create(config=config)
        try:
            try:
                # Open the target page
                tab = await browser.get("https://aternos.org/go")
                
                # Log in
                input_username = await tab.select("input[placeholder='Username']", timeout=4)
                await input_username.send_keys("StarterBot")
                
                input_password = await tab.select("input[placeholder='••••••••']")
                await input_password.send_keys("BotAccount")
                
                login_button = await tab.select("button[title='Login']")
                await login_button.click()
            except:
                pass

            # Handle cookies consent if present
            try:
                cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=4)
                await cookies.click()
            except:
                pass

            # Select the server
            server_select = await tab.select('div[title="roadblocksjailbrokey"]', timeout=1000)
            await server_select.click()

            # Open logs page
            logs_button = await tab.select('a[title="Log"]', timeout=20)
            await logs_button.click()

            await process_logs(tab, client, pending_responses, linked_accounts, console_queue)
            

        finally:
            try:
                if tab:
                    await tab.close()
                if browser.connection:
                    await browser.connection.aclose()
                browser.stop()
            except Exception as e:
                print(f"Error during browser closure: {e}")
            finally:
                if browser._process:
                    browser._process.terminate()
                    await browser._process.wait()


async def check_logs(tab: nodriver.Tab):
    """Fetch and return all log entries from the page."""
    try:
        # Select the log entries
        try:
            log_elements = await tab.select_all('div#console.out[data-pip-scroll="bottom"] div.line')
        except:
            return []
        
        log_entries = []
        for element in log_elements:
            clean_log = BeautifulSoup(str(element), "html.parser").get_text(separator=' ', strip=True)
            log_entries.append(clean_log)
        return log_entries
    except Exception as e:
        print(f"Error occurred while fetching logs: {e}")
        return []

async def extract_login_info(log):
    """Extract the player username and IP address from a login log entry."""
    # Regex pattern to match the username and IP address
    pattern = r'\[.*?\]: (\S+)\[/(\d+\.\d+\.\d+\.\d+):\d+\] logged in with entity id'
    print("is this thing on or what")
    
    match = re.search(pattern, log)
    
    if match:
        username = match.group(1)  # The player username
        ip_address = match.group(2)  # The IP address
        print("username and ip being returned.")
        return username, ip_address
    print("none being returned, username and ip could not be found..?")
    return None, None
async def send_ip_mismatch_dm(username, ip, client, pending_responses, linked_accounts):
    try:
        user = await client.fetch_user(linked_accounts[username.lower()])
        await user.send(f"Was this you? Someone just logged onto the MC account {username} using the IP address {ip}. If this was you, please REPLY TO THIS MESSAGE and say yes. Just that. If not, please reply and say no, or don't reply at all.")
        pending_responses.append([user.id, ip])
        save_pending_responses(pending_responses)
    except KeyError:
        print(f"User {username} not linked to discord.")

async def process_logs(tab: nodriver.Tab, client, pending_responses, linked_accounts, console_queue: asyncio.Queue):
    """Process the logs and check for player login messages."""
    global last_checked_log
    while True:
        log_entries = await check_logs(tab)
        for log in reversed(log_entries):
            if log != last_checked_log:
                if "logged in with entity id" in log:
                    print(log)
                    username, ip_address = await extract_login_info(log)
                    print(f"Detected login: {username} from IP {ip_address}, detected city as {HostIP.get(ip_address=ip_address).city}")
                    try:
                        correct_ip = player_ip_addresses[username]
                    except KeyError:
                        player_ip_addresses[username] = [ip_address]
                        save_correct_ip_addresses(player_ip_addresses)
                        correct_ip = ip_address
                    if ip_address not in correct_ip:
                        print("FRADULENT LOGIN")
                        await console_queue.put({"action": "command", "text": f"ban-ip {ip_address}"})
                        await send_ip_mismatch_dm(username, ip_address, client, pending_responses, linked_accounts)
            else:
                break
        last_checked_log = None
        for entry in reversed(log_entries):
            entry = entry.strip()
            if entry.startswith('['):
                last_checked_log = entry
                break
        save_last_checked_log(last_checked_log)
        
        # Wait for the refresh interval before checking again
        await asyncio.sleep(1.5)  # Refresh interval (1.5 seconds)

async def get_console(queue: asyncio.Queue, client, pending_responses, linked_accounts):
    with Display():
        print("console is being opened")
        while True:  # Outer loop to handle reconnection
            try:
                # Check if server is online before opening browser
                server_state = await starting_server(False)
                if not server_state:  # Server is off
                    await asyncio.sleep(30)  # Wait before checking again
                    continue

                config = nodriver.Config(browser_executable_path="chromium-mac/Chromium.app/Contents/MacOS/Chromium")
                browser = await nodriver.Browser.create(config=config)
                try:
                    # Open the target page
                    tab = await browser.get("https://aternos.org/go")
                    
                    # Log in
                    try:
                        input_username = await tab.select("input[placeholder='Username']")
                        await input_username.send_keys("StarterBot")
                        
                        input_password = await tab.select("input[placeholder='••••••••']")
                        await input_password.send_keys("BotAccount")
                        
                        login_button = await tab.select("button[title='Login']")
                        await login_button.click()
                    except:
                        pass

                    # Handle cookies consent if present
                    try:
                        cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=10)
                        await cookies.click()
                    except:
                        pass

                    # Select the server
                    server_select = await tab.select('div[title="roadblocksjailbrokey"]', timeout=1000)
                    await server_select.click()
                    await asyncio.sleep(2)
                    await browser.get("https://aternos.org/server/#goog_rewarded")
                    try:
                        cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=10)
                        await cookies.click()
                    except:
                        pass
                    await browser.get("https://aternos.org/server/#goog_rewarded")
                    console = await tab.select("a[title='Console'] span[class='navigation-item-label']")
                    await console.click()
                    await asyncio.sleep(3)
                    await browser.get("https://aternos.org/console/#goog_rewarded")
                    command_entry = await tab.select('#c-input', timeout=30)
                    await asyncio.sleep(1.5)

                    try:
                        cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=10)
                        await cookies.click()
                    except:
                        pass
                    logs = asyncio.create_task(process_logs(tab, client, pending_responses, linked_accounts, queue))
                            
                    iteration_count = 0
                    while True:
                        await asyncio.sleep(1)
                        print(f"iteration count: {iteration_count}")
                        # Check server status every 10 iterations
                        if iteration_count % 10 == 0:
                            print("checking server state")
                            server_state = await starting_server(False)
                            print(f"server state: {server_state}")
                            if not server_state:  # Server is off
                                print("Server detected as offline, closing console tab")
                                raise Exception("Server went offline")
                        
                        iteration_count += 1
                        command = await queue.get()
                        if command["action"] == "command":
                            await command_entry.send_keys(command["text"])
                            await asyncio.sleep(0.1)
                            await tab.evaluate("""
                            document.getElementById('c-input').dispatchEvent(new KeyboardEvent('keyup', { keyCode: 13, key: 'Enter' }));
    """)

                finally:
                    try:
                        if tab:
                            await tab.close()
                        if browser.connection:
                            await browser.connection.aclose()
                        browser.stop()
                    except Exception as e:
                        print(f"Error during browser closure: {e}")
                    finally:
                        if browser._process:
                            browser._process.terminate()
                            await browser._process.wait()
                        
            except Exception as e:
                print(f"Console session ended: {e}")
                await asyncio.sleep(30)  # Wait before attempting to reconnect

async def maintain_server_tab():
    with Display():
        config = nodriver.Config(browser_executable_path="chromium-mac/Chromium.app/Contents/MacOS/Chromium")
        browser = await nodriver.Browser.create(config=config)
        print("Starting server monitoring tab")
        try:
            # Open the target page
            tab = await browser.get("https://aternos.org/go")
            
            # Log in
            try:
                input_username = await tab.select("input[placeholder='Username']")
                await input_username.send_keys("StarterBot")
                
                input_password = await tab.select("input[placeholder='••••••••']")
                await input_password.send_keys("BotAccount")
                
                login_button = await tab.select("button[title='Login']")
                await login_button.click()
            except:
                pass

            # Handle cookies consent if present
            try:
                cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=10)
                await cookies.click()
            except:
                pass

            # Select the server
            server_select = await tab.select('div[title="roadblocksjailbrokey"]', timeout=1000)
            await server_select.click()
            await asyncio.sleep(1.5)
            await browser.get("https://aternos.org/server/#goog_rewarded")
            try:
                cookies = await tab.select('#theme-switch > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button', timeout=5)
                await cookies.click()
            except:
                pass
            print("okay made it to the while true")
            while True:
                try:
                    command = await server_queue.get()
                    if command["action"] == "start_server":
                        status_element = await tab.select(".statuslabel-label", timeout=5)
                        status_text = status_element.text
                        if "offline" not in status_text.lower(): 
                            print("server is already running, not starting now")
                            await command["response_queue"].put({"start_time": False})
                            continue
                        start_time = get_time()
                        # Find and click the start button
                        start_button = await tab.select("#start")
                        if start_button:
                            await start_button.click()
                            print("Server start initiated")
                        else:
                            print("couldn't find start button")
                            await command["response_queue".put({"start_time": False})]
                            continue
                        status_element = await tab.select(".statuslabel-label", timeout=5)
                        status_text = status_element.text
                        while "online" not in status_text.lower():
                            await asyncio.sleep(0.1)
                            status_text = await tab.select(".statuslabel-label", timeout=5)
                            status_text = status_text.text
                        await command["response_queue"].put({"start_time": get_time()-start_time})
                    elif command["action"] == "check_status":
                        # Check if server is running by looking for specific elements
                        try:
                            status_element = await tab.select(".statuslabel-label", timeout=5)
                            status_text = status_element.text.strip()
                            print(status_text)
                            is_online = "online" in status_text.lower()
                            await command["response_queue"].put({"server_online": is_online})
                        except Exception as e:
                            print(f"Error checking server status: {e}")
                            await command["response_queue"].put({"server_online": False})
                    await asyncio.sleep(0.75)


                except KeyboardInterrupt:
                    print("Code keyboard interrupted.")
                    break

                except Exception as e:
                    print(f"Error in server tab: {e}")
                    await asyncio.sleep(1)

        finally:
            try:
                if tab:
                    await tab.close()
                if browser.connection:
                    await browser.connection.aclose()
                browser.stop()
            except Exception as e:
                print(f"Error during browser closure: {e}")
            finally:
                if browser._process:
                    browser._process.terminate()
                    await browser._process.wait()

async def check_server_status():
    print("checking server status")
    response_queue = asyncio.Queue()
    await server_queue.put({
        "action": "check_status",
        "response_queue": response_queue
    })
    result = await response_queue.get()
    return result["server_online"]

async def start_server():
    response_queue = asyncio.Queue()
    await server_queue.put({
        "action": "start_server",
        "response_queue": response_queue
    })
    result = await response_queue.get()
    return result["start_time"]

if __name__ == '__main__':
    asyncio.run(maintain_server_tab())
    asyncio.run(maintain_players_tab())
    # ok THIS is the last testing comment. promise.