import unittest
from hashlib import sha256
from pathlib import Path

from playwright.sync_api import Error, sync_playwright


def page_error(exception: Error) -> None:
    raise exception


class TestWebApplication(unittest.TestCase):
    def setUp(self: "TestWebApplication") -> None:
        self.input_nii_file_path = Path("tmp/masks-multiclass.nii")
        if not self.input_nii_file_path.is_file():
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page()
                page.goto(
                    "https://github.com/pbizopoulos/semi-automatic-annotation-tool/releases/latest",
                )
                page.click("text=Assets")
                with page.expect_download() as download_info:
                    page.click("text=masks-multiclass.nii")
                download = download_info.value
                download.save_as(self.input_nii_file_path)
                browser.close()

    def test_web_application(self: "TestWebApplication") -> None:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(record_video_dir="tmp/")
            page = context.new_page()
            timeout = 200000
            page.set_default_timeout(timeout)
            page.set_default_navigation_timeout(timeout)
            page.on("pageerror", page_error)
            page.goto("https://convert-nifti-to-glb.incisive.iti.gr/")
            page.set_input_files(
                "#load-nifti-file-input-file",
                self.input_nii_file_path.resolve().as_posix(),
            )
            with page.expect_download() as download_info:
                page.click("#convert-button")
            download = download_info.value
            download.save_as("tmp/masks-multiclass-step-size-2-iterations-1.glb")
            with Path("tmp/masks-multiclass-step-size-2-iterations-1.glb").open(
                "rb",
            ) as file:
                assert (
                    sha256(file.read()).hexdigest()
                    == "5eb4b65bf995f07078a7452c6407ad1746cbe0c19306802fef5fdae2b7ef7580"  # noqa: E501
                )
            page.screenshot(path="tmp/screenshot.png")
            with Path("tmp/screenshot.png").open("rb") as file:
                assert (
                    sha256(file.read()).hexdigest()
                    == "508ac6b1ae30a85f641f96c815dcad9e23deb2885024b04a614c25e7114a3e76"  # noqa: E501
                )
            context.close()
            browser.close()


if __name__ == "__main__":
    unittest.main()
