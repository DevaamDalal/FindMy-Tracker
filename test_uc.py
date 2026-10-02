import undetected_chromedriver as uc
print('testing')
try:
    driver = uc.Chrome(version_main=153)
    print('success')
    driver.quit()
except Exception as e:
    print(f'Error: {e}')

