import hashlib
from os.path import isfile, join

from playwright.sync_api import sync_playwright


def main():
    input_nii_file_path = join('bin', 'masks-multiclass.nii')
    if not isfile(input_nii_file_path):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto('https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/latest')
            page.click('text=Assets')
            with page.expect_download() as download_info:
                page.click('text=masks-multiclass.nii')
            download = download_info.value
            download.save_as(input_nii_file_path)
            browser.close()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(record_video_dir='bin/')
        page = context.new_page()
        timeout = 200000
        page.set_default_timeout(timeout)
        page.set_default_navigation_timeout(timeout)
        page.on('pageerror', lambda exception: (_ for _ in ()).throw(Exception(f'uncaught exception: {exception}')))
        page.goto('https://nifti-to-glb-conversion-tool.incisive.iti.gr/')
        page.set_input_files('#load-nifti-file-input-file', input_nii_file_path)
        with page.expect_download() as download_info:
            page.click('#convert-button')
        download = download_info.value
        download.save_as(join('bin', 'masks-multiclass-step-size-2-iterations-1.glb'))
        with open(join('bin', 'masks-multiclass-step-size-2-iterations-1.glb'), 'rb') as file:
            assert hashlib.sha256(file.read()).hexdigest() == 'a0a64cb2193fb0919525c51e6f83fe7811c6bd42f93481c0c6cfce204a81eaad'
        page.screenshot(path=join('bin', 'screenshot.png'))
        with open(join('bin', 'screenshot.png'), 'rb') as file:
            assert hashlib.sha256(file.read()).hexdigest() == 'eeeead05d8dcadce69848e1959d7b2d31dbee24eb75604363bcb8ee69e556104'
        context.close()
        browser.close()


if __name__ == '__main__':
    main()
