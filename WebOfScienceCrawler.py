# @author Paris
# @date 2024/8/22
# selenium = 4.23.1
from time import sleep
import random
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# 获取Chrome驱动的路径
driver_path = ChromeDriverManager().install()
print(driver_path)
# 创建Chrome浏览器的服务实例
service = Service(executable_path=driver_path)

options = Options()
# 设置用户代理
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
options.add_argument(f'user-agent={user_agent}')
# 禁用图片加载以加快速度
options.add_argument('--disable-images')
# 忽略证书错误
options.add_argument('--ignore-certificate-errors')
# 忽略 Bluetooth: bluetooth_adapter_winrt.cc:1075 Getting Default Adapter failed. 错误
options.add_experimental_option('excludeSwitches', ['enable-automation'])
# 忽略 DevTools listening on ws://127.0.0.1... 提示
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# 更改浏览器的其他标识,防止反爬
options.add_argument('--disable-blink-features=AutomationControlled')  # 防止webdriver属性被检测
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-infobars')
options.add_argument("user-data-dir=C:/Users/User/AppData/Local/Google/Chrome/User Data") #add chrome profile for authentication easiness, change this acording to your chrome profile directory!


#-----------------------------《参数调整区域》----------------------------------------#
totalDocumentNumber=12345 #预先指定爬取数量 , max 100000 it seems...

url="https://webofscience.clarivate.cn/wos/woscc/summary/XXXXXXXXXXX/relevance/1"#获取数据的URL，请先检索出想要的数据再复制检索结果页面的url粘贴到这里


# 模式设置
mode = "Full Record" # 完整记录
maxNumber = 1000
downloadBatchNum = (totalDocumentNumber // maxNumber) + 1
startBatchNum = 40  #无故中断时，观察Downloading records，重新开始下载，设置为0，则下载第0001-1000条
endFlag=False
#-----------------------------《参数调整区域》----------------------------------------#

def random_sleep(min_time=2, max_time=5):
    """随机睡眠一段时间"""
    sleep_time = random.uniform(min_time, max_time)
    print(f"休眠 {sleep_time:.2f} 秒")
    sleep(sleep_time)
def get_current_mouse_position(driver):
    """获取当前鼠标位置"""
    return driver.execute_script("return { x: window.scrollX + window.innerWidth / 2, y: window.scrollY + window.innerHeight / 2 };")

def human_like_mouse_move(driver):
    """模拟人类的鼠标移动"""
    action = ActionChains(driver)
    current_position = get_current_mouse_position(driver)
    for _ in range(3):  # 随机移动几次
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        try:
            action.move_by_offset(x_offset, y_offset).perform()
            random_sleep(0.5, 1.5)
        except selenium.common.exceptions.MoveTargetOutOfBoundsException:
            # print(f"移动目标超出边界：x_offset={x_offset}, y_offset={y_offset}")
            pass
            # 处理异常情况，可能尝试重新定位
def human_like_scroll(driver):
    """模拟人类的滚动操作"""
    scroll_height = random.randint(100, 500)
    driver.execute_script(f"window.scrollBy(0, {scroll_height});")
    # print(f"向下滚动了 {scroll_height} 像素")
    random_sleep(0.5, 2.0)

# 使用服务实例创建WebDriver对象
driver = webdriver.Chrome(service=service,options=options)
# print(type(driver))

# while(True):
try:
    for currentBatch in range(startBatchNum,downloadBatchNum):
        #导出不同的batch时，每次都再刷新一下
        # driver.get(url+"(overlay:export/ext)")  #设置导出为(Tab Delimited File)TXT格式
        #driver.get(url + "(overlay:export/exbt)")  # Set to export as bibtex format
        driver.get(url + "(overlay:export/exc)")  #设置导出为EXCEL格式
        sleepTime=random.sample(range(15,21),1)
        print("休眠" + str(sleepTime[0]) + "秒! 等待刷新结果显示!")
        sleep(sleepTime[0])

        human_like_mouse_move(driver)  # 模拟鼠标移动
        human_like_scroll(driver)      # 模拟页面滚动

        if currentBatch == startBatchNum:
            # 关闭一些弹框 例如接受Cookie、人机验证
            try:
                # 设置等待的超时时间
                wait = WebDriverWait(driver, 5)  # 5秒超时时间
                # 等待一个元素变得可见并且可点击
                element = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                element.click()
                print("成功点击：接受所有Cookie")
            except TimeoutException:
                # 如果等待超时，执行这里的代码
                print("等待超时，无需接受Cookie")
            except NoSuchElementException:
                # 如果元素不存在，执行这里的代码
                print("没有找到Cookie元素")

            try:
                # 设置等待的超时时间
                wait = WebDriverWait(driver, 5)  # 5秒超时时间
                # 等待一个元素变得可见并且可点击
                element = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div[2]/div/mat-dialog-container/app-captcha-details/div/div/div/p")))  # 识别人机验证
                if element is not None:
                    print("请60秒内完成人机验证！！！")
                    sleep(60)  # 60秒超时时间
            except TimeoutException:
                # 如果等待超时，执行这里的代码
                print("等待超时，无需或未进行人机验证")
            except NoSuchElementException:
                # 如果元素不存在，执行这里的代码
                print("没有人机验证元素")
        else:
            pass

        #确定每次导出时，起始与终止记录数值
        startNum = currentBatch * maxNumber + 1
        if currentBatch!=downloadBatchNum-1:
            EndNum=(currentBatch+1)*maxNumber
        else:
            EndNum = totalDocumentNumber
        #点选：选择记录选项
        labelElements=driver.find_elements(By.XPATH, "//label[@for='radio3-input']")
        labelElements[0].click()
        #确定起始记录
        inputElements_1=driver.find_elements(By.XPATH, "//input[@type='text']")
        inputElements_1[0].clear()
        inputElements_1[0].send_keys(str(startNum))
        #确定终止记录
        inputElements_2=driver.find_elements(By.XPATH, "//input[@type='text']")
        inputElements_2[1].clear()
        inputElements_2[1].send_keys(str(EndNum))
        closeButtonElements_1 = driver.find_elements(By.XPATH, "//button[@class='_pendo-close-guide']")
        print("Sleeping for 2 seconds! Waiting for download button ready!") # i think sometimes button not ready and it throws an error not downloading 
        sleep(2)
        if len(closeButtonElements_1) > 0:
            closeButtonElements_1[0].click()
        #点击记录内容下拉框
        dropdownElements = driver.find_elements(By.XPATH, "//button[@class='dropdown']")
        dropdownElements[0].click()
        closeButtonElements_1 = driver.find_elements(By.XPATH, "//button[@class='_pendo-close-guide']")
        if len(closeButtonElements_1) > 0:
            closeButtonElements_1[0].click()
        fullRecordsElements = driver.find_elements(By.XPATH, "//div[@title='"+mode+"']")##WOS最易修改之处
        fullRecordsElements[0].click()
        closeButtonElements_1=driver.find_elements(By.XPATH, "//button[@class='_pendo-close-guide']")
        if len(closeButtonElements_1) > 0:
            closeButtonElements_1[0].click()
        #点击导出
        exportElements=driver.find_elements(By.XPATH, "//button[@class='mat-focus-indicator mat-flat-button mat-button-base mat-primary']")
        exportElements[0].click()
        sleep(5)
        captchaElements = driver.find_elements(By.XPATH, "//app-captcha-details[@class='ng-star-inserted']")
        if len(captchaElements)>0:
            startBatchNum = currentBatch
            print("请设置startBatchNum为"+str(startBatchNum)+"重新开始")
            driver.close()
            break
        else:
            try:
                print("Downloading records:"+str(startNum)+"~"+str(EndNum)+"!")
                #注意间隔时间要足够长，不然容易出现问题
                sleepTime = random.sample(range(20, 50),1)
                print("休眠" + str(sleepTime[0]) + "秒! 等待下载完成!")
                sleep(sleepTime[0])
                # 设置最长等待时间
                wait = WebDriverWait(driver, 200)
                # 等待直到指定元素消失
                wait.until(EC.invisibility_of_element((By.XPATH, "//button[@class='mat-focus-indicator mat-flat-button mat-button-base mat-primary']")))
                # 元素消失后的操作
                print("下载完成,准备下载新文件！！！")
            finally:
                pass

        if currentBatch==downloadBatchNum-1:
            endFlag=True
    if endFlag==True:
        print("爬取完毕！")
        # break
except Exception as e:
    print(f"发生异常：{e}")
    input("发生错误，按回车键继续...")

finally:
    input("爬取完毕或遇到异常，浏览器窗口保留。按回车键关闭浏览器...")
# 关闭浏览器
driver.quit()
