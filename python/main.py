import unittest
from hashlib import sha256
from pathlib import Path

from playwright.sync_api import Error, sync_playwright


class TestWebApplication(unittest.TestCase):
    def setUp(self: "TestWebApplication") -> None:
        self.input_nii_file_path = Path("data/masks-multiclass.nii")
        if not self.input_nii_file_path.is_file():
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                page.goto("https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/latest")
                page.click("text=Assets")
                with page.expect_download() as download_info:
                    page.click("text=masks-multiclass.nii")
                download = download_info.value
                download.save_as(self.input_nii_file_path)
                browser.close()

    def test_web_application(self: "TestWebApplication") -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(record_video_dir="bin/")
            page = context.new_page()
            timeout = 200000
            page.set_default_timeout(timeout)
            page.set_default_navigation_timeout(timeout)
            page.on("pageerror", page_error)
            page.goto("https://nifti-to-glb-conversion-tool.incisive.iti.gr/")
            page.set_input_files("#load-nifti-file-input-file", self.input_nii_file_path.resolve().as_posix())
            with page.expect_download() as download_info:
                page.click("#convert-button")
            download = download_info.value
            download.save_as("bin/masks-multiclass-step-size-2-iterations-1.glb")
            with Path("bin/masks-multiclass-step-size-2-iterations-1.glb").open("rb") as file:
                assert sha256(file.read()).hexdigest() == "bb5e6fc4d4d0be5009a6a8cf8794b4bee566ff39090288de0934534368e2af9f"
            page.screenshot(path="bin/screenshot.png")
            with Path("bin/screenshot.png").open("rb") as file:
                assert sha256(file.read()).hexdigest() == "84d1ca92c1f2daba3a11323fc17fe40607f0eb56d6cf78e3f83d9ae21a6eefdb"
            context.close()
            browser.close()


def page_error(exception: Error) -> None:
    raise exception


if __name__ == "__main__":
    unittest.main()
