import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE="http://127.0.0.1:8000"
OUT=Path("qa/screenshots")
OUT.mkdir(parents=True,exist_ok=True)

async def run():
  outcomes=[]
  async with async_playwright() as p:
    browser=await p.chromium.launch(headless=True,args=["--no-sandbox"])
    for width,height,label in [(320,740,"compact"),(390,844,"mobile"),(768,900,"tablet"),(1024,768,"laptop"),(1440,900,"desktop")]:
      context=await browser.new_context(viewport={"width":width,"height":height},accept_downloads=True,reduced_motion="reduce")
      page=await context.new_page()
      errors=[]
      page.on("pageerror",lambda error:errors.append(str(error)))
      await page.goto(BASE,wait_until="domcontentloaded",timeout=30000)
      await page.wait_for_timeout(1800)
      await page.locator("#view-routines").wait_for(state="visible",timeout=10000)
      metrics=await page.evaluate("""() => ({viewport:innerWidth,root:document.documentElement.scrollWidth,body:document.body.scrollWidth,hero:document.querySelector('.lumina-hero').getBoundingClientRect().width,nav:!!document.querySelector('.bottom-nav')})""")
      assert metrics["root"]<=width+2,(label,"horizontal overflow",metrics)
      assert metrics["hero"]>200,(label,"hero too narrow",metrics)
      assert await page.locator("#luminaRoutinesDone").inner_text()!="",(label,"missing summary")
      if width<=768:
        more=page.locator("#luminaMoreButton")
        assert await more.is_visible(),(label,"More missing")
        await more.click()
        assert await page.locator("#luminaMoreMenu").is_visible(),(label,"More panel hidden")
        await page.locator('#luminaMoreMenu button:has-text("Wellness")').click()
        assert await page.locator("#view-wellness").is_visible(),(label,"Wellness not reachable")
      await page.evaluate("setView('calendar')")
      await page.locator("#view-calendar").wait_for(state="visible")
      await page.evaluate("setCalMode('month')")
      assert await page.locator("#monthGrid .month-cell").count()>=28,(label,"month days missing")
      await page.evaluate("setCalMode('week')")
      assert await page.locator(".week-calendar-header").is_visible()
      widths=await page.evaluate("""() => ({a:document.getElementById('weekHeader').getBoundingClientRect().width,b:document.querySelector('.week-grid').getBoundingClientRect().width})""")
      assert abs(widths["a"]-widths["b"])<3,(label,"misaligned week header",widths)
      if width<=768:
        await page.evaluate("document.getElementById('luminaWeekScroll').scrollLeft=240")
        assert await page.evaluate("document.getElementById('luminaWeekScroll').scrollLeft")>100,(label,"week scroll broken")
      await page.evaluate("setView('lists')")
      await page.locator("#listInput").fill("Test oats & milk")
      await page.locator("#listInput").press("Enter")
      assert await page.locator("#shoppingListDisplay").get_by_text("Test oats & milk").count()==1,(label,"list entry failed")
      await page.reload(wait_until="domcontentloaded")
      await page.wait_for_timeout(450)
      await page.evaluate("setView('lists')")
      assert await page.locator("#shoppingListDisplay").get_by_text("Test oats & milk").count()==1,(label,"list not retained")
      await page.evaluate("setView('routines')")
      if label in ("desktop","mobile","compact"):
        await page.screenshot(path=str(OUT/(label+"-dashboard.png")),full_page=False)
      if label=="mobile":
        await page.evaluate("setView('calendar');setCalMode('month')")
        await page.screenshot(path=str(OUT/"mobile-calendar.png"),full_page=False)
      assert not errors,(label,"page errors",errors)
      outcomes.append({"viewport":label,"width":width,"layout":"pass","calendar":"pass","persistence":"pass","pageErrors":errors})
      await context.close()
    await browser.close()
  (OUT/"results.json").write_text(json.dumps(outcomes,indent=2))
  print(json.dumps(outcomes,indent=2))

if __name__=="__main__":
 asyncio.run(run())
