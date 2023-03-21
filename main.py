from hashlib import sha256
from pathlib import Path

from playwright.sync_api import Error, sync_playwright


def main() -> None:
    input_nii_file_path = Path("bin/masks-multiclass.nii")
    if not input_nii_file_path.is_file():
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto("https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/latest")
            page.click("text=Assets")
            with page.expect_download() as download_info:
                page.click("text=masks-multiclass.nii")
            download = download_info.value
            download.save_as(input_nii_file_path)
            browser.close()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(record_video_dir="bin/")
        page = context.new_page()
        timeout = 200000
        page.set_default_timeout(timeout)
        page.set_default_navigation_timeout(timeout)
        page.on("pageerror", page_error)
        page.goto("https://nifti-to-glb-conversion-tool.incisive.iti.gr/")
        page.set_input_files("#load-nifti-file-input-file", input_nii_file_path.resolve().as_posix())
        with page.expect_download() as download_info:
            page.click("#convert-button")
        download = download_info.value
        download.save_as("bin/masks-multiclass-step-size-2-iterations-1.glb")
        with Path("bin/masks-multiclass-step-size-2-iterations-1.glb").open("rb") as file:
            assert sha256(file.read()).hexdigest() == "a0a64cb2193fb0919525c51e6f83fe7811c6bd42f93481c0c6cfce204a81eaad"
        page.screenshot(path="bin/screenshot.png")
        with Path("bin/screenshot.png").open("rb") as file:
            assert sha256(file.read()).hexdigest() == "947b85dcf07c39fd78ad776b165d22e9a9d595191d37e02ae3abfbf09e0f859c"
        context.close()
        browser.close()


def page_error(exception: Error) -> None:
    raise exception


if __name__ == "__main__":
    main()
