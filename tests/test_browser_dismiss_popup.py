
from agent.browser import Browser

class FakeLocator:
    def __init__(self, is_visible_result: bool = False, throw_on_visible: bool = False) -> None:
        self.clicked = False
        self._is_visible_result = is_visible_result
        self._throw_on_visible = throw_on_visible

    @property
    def first(self) -> 'FakeLocator':
        return self

    def is_visible(self, timeout: int) -> bool:
        if self._throw_on_visible:
            raise Exception("Mocked exception during is_visible")
        return self._is_visible_result

    def click(self, timeout: int) -> None:
        self.clicked = True


class FakePage:
    def __init__(self, visible_selector: str | None = None, throw_on_selector: str | None = None) -> None:
        self.visible_selector = visible_selector
        self.throw_on_selector = throw_on_selector
        self.locators: dict[str, FakeLocator] = {}

    def locator(self, selector: str) -> FakeLocator:
        if selector not in self.locators:
            is_visible = self.visible_selector and self.visible_selector in selector
            throw_on_visible = self.throw_on_selector and self.throw_on_selector in selector
            self.locators[selector] = FakeLocator(is_visible_result=is_visible, throw_on_visible=throw_on_visible)
        return self.locators[selector]


class FakeBrowser(Browser):
    def __init__(self, page: FakePage) -> None:
        super().__init__()
        self.page = page
        self.settle_called = False

    def _page(self) -> FakePage:
        return self.page

    def _settle(self, network_idle_ms: int = 2500) -> None:
        self.settle_called = True


def test_dismiss_popup_success():
    target_selector = ".close-button"
    page = FakePage(visible_selector=target_selector)
    browser = FakeBrowser(page)

    result = browser.dismiss_popup()

    assert result["ok"] is True
    assert result["message"] == "dismissed popup"
    assert result["data"]["selector"] == "combined-popup-selector"
    assert browser.settle_called is True

    # Verify it clicked the correct locator
    clicked_locators = [loc for loc in page.locators.values() if loc.clicked]
    assert len(clicked_locators) == 1


def test_dismiss_popup_not_found():
    page = FakePage(visible_selector=None)
    browser = FakeBrowser(page)

    result = browser.dismiss_popup()

    assert result["ok"] is True
    assert result["message"] == "no common popup found"
    assert result["data"] == {}
    assert browser.settle_called is False

    # Verify no locators were clicked
    for loc in page.locators.values():
        assert loc.clicked is False


def test_dismiss_popup_exception():
    target_selector = "button[aria-label='Close']"
    page = FakePage(throw_on_selector=target_selector)
    browser = FakeBrowser(page)

    result = browser.dismiss_popup()

    assert result["ok"] is False
    assert result["message"] == "dismiss_popup failed"
    assert "Mocked exception during is_visible" in str(result["data"]["error"])
    assert browser.settle_called is False
