import os, random, zipfile, time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    import requests, tqdm
except ImportError:
    input(f'Вы не установили нужных библиотек. Нажмите Enter для их автоматической установки.')
    os.system('pip install selenium')
    os.system('pip install webdriver_manager')
    os.system('pip install requests')
    os.system('pip install tqdm')

query = input(f'А какой запрос?..:')
colichestvo = int(input(f'Сколько надо картинок?..:'))
scrolly = int(input(f'Сколько скроллов делать?: '))
directory = input(f'Куда сохранять это все?: ')

if not os.path.exists(directory):
    os.makedirs(directory)

os.chdir(directory)

def create_proxy_auth_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
    """Создаём плагин для авторизации прокси"""
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    chrome.webRequest.onAuthRequired.addListener(
        function(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        },
        {urls: ["<all_urls>"]},
        ['blocking']
    );
    """ % (proxy_host, proxy_port, proxy_user, proxy_pass)

    # Создаём временный файл плагина
    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    
    return plugin_file

def parse_yandex_images(query, max_images=10, scrolly: int = 5):
    try:
        proxy_plugin = create_proxy_auth_extension('...', 0000, '...', '...')
        # Настраиваем Chrome
        chrome_options = Options()
        chrome_options.add_extension(proxy_plugin)
        chrome_options.add_argument("--log-level=1")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("Браузер запустился, пиздец")
    except Exception as e:
        print(f"Не могу запустить Chrome, пиздец: {e}")
        return

    try:
        url = f"https://yandex.ru/images/search?text={query}&isize=large"
        driver.get(url)
        print("Зашёл на страницу, ждём, блять")
        time.sleep(5)  # Даём больше времени на загрузку

        # Скроллим вниз
        for _ in range(scrolly):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print("Скроллю, сука")
        all_images = driver.find_elements(By.TAG_NAME, "img")[:max_images]
        print(f"Всего тегов <img> на странице: {len(all_images)}")
        if all_images:
            print("Начинаем качать картинки...")
            for img in tqdm.tqdm(all_images, desc='Качаем картинки...', ncols=70):
                img_url = img.get_attribute("src")
                if img_url and "http" in img_url:
                    try:
                        _ = random.random()
                        file = open(directory + f'{_}.jpg', 'wb')
                        file.write(requests.get(img_url, proxies={"http": "http://...:...@...:0000", "https": "http://...:...@...:0000"}, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}).content)
                        file.close()
                    except:
                        pass
        else:
            print("Ни одного <img> не нашёл, пиздец полный")
        driver.quit()
        print("Браузер закрыл, пиздец, готово")
        os.remove('proxy_auth_plugin.zip')

    except Exception as e:
        print(f"Что-то пошло по пизде: {e}")
        os.remove('proxy_auth_plugin.zip')

if __name__ == '__main__':
    parse_yandex_images(query, colichestvo, scrolly=scrolly)