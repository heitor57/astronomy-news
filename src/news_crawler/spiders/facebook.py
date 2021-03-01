import time
import selenium
def facebook_process(driver):
    js = """arguments[0].scrollIntoView(
{
            behavior: 'auto',
            block: 'center',
            inline: 'center'
}
    )"""
    try:
        element = driver.find_element_by_xpath("//button[@class='_1gl3 _4jy0 _4jy3 _517h _51sy _42ft']")
        while element:
            driver.execute_script(js, element)
            time.sleep(0.2)
            element.click()
            time.sleep(2)
            element = driver.find_element_by_xpath("//button[@class='_1gl3 _4jy0 _4jy3 _517h _51sy _42ft']")
    except selenium.common.exceptions.NoSuchElementException as e:
        pass

    try:
        element = driver.find_element_by_xpath("//div[@class='_5yct _3-8y _3-96 _2ph-']//a")
        while element:
            driver.execute_script(js, element)
            time.sleep(0.2)
            element.click()
            time.sleep(2)
            element = driver.find_element_by_xpath("//div[@class='_5yct _3-8y _3-96 _2ph-']//a")
    except selenium.common.exceptions.NoSuchElementException as e:
        pass
