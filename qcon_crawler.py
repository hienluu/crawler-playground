import asyncio
import argparse
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter


async def crawl_llm(url: str):
    print("==========crawl_llm==============")
    browser_config = BrowserConfig(headless=True)  # Default browser configuration
   
   
    raw_md_generator = DefaultMarkdownGenerator(            
            options={"ignore_links": True},
         )
    
    print("==========raw_md_generator.content_source==============")
    print(raw_md_generator.content_source)
    
    print("==========raw_md_generator.options==============")
    print(raw_md_generator.options)
    
    run_config = CrawlerRunConfig(
         
    )   # Default crawl run configuration

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
    
    print(f"==========result.success: {result.success} ==============")
    print(f"==========result.status_code: {result.status_code} ==============")
    
    return result.markdown
    


async def crawl_page(url: str):
    print("==========crawl_page==============")
    browser_config = BrowserConfig(headless=True, text_mode=True)  # Default browser configuration
   
    raw_md_generator = DefaultMarkdownGenerator(
            content_source="cleaned_html",
            options={
                "ignore_links": True,
                "ignore_images": True,
                "escape_html": False,               
            },          
    )
    
    print("==========raw_md_generator.content_source==============")
    print(raw_md_generator.content_source)

    
    print("==========raw_md_generator.options==============")
    print(raw_md_generator.options)
    
    run_config = CrawlerRunConfig(      
        excluded_tags=['form', 'header', 'footer', 'nav'],
        markdown_generator=raw_md_generator,
        cache_mode=CacheMode.BYPASS,
        #exclude_external_links=True

    )   # Default crawl run configuration

    print("==========run_config==============")
    print(f"run_config.target_elements: {run_config.target_elements}")
    print(f"run_config.excluded_tags: {run_config.excluded_tags}")
    print(f"run_config.css_selector: {run_config.css_selector}")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_config
        )
    
    print(f"==========result.success: {result.success} ==============")
    print(f"==========result.status_code: {result.status_code} ==============")
    
    if result.success:
     title = result.metadata.get("title", "No title found")
     print(f"The title of '{url}' is: {title}")
    else:
        print(f"Failed to crawl '{url}'.")
    
    return result.markdown

def is_sitemap(url: str) -> bool:
    return url.endswith('sitemap.xml') or 'sitemap' in urlparse(url).path

def is_txt(url: str) -> bool:
    return url.endswith('.txt')

def main(url: str, output_file: str):
    result_content = ""
    if (is_txt(url)):
        result_content = asyncio.run(crawl_llm(url))
    else:
        result_content = asyncio.run(crawl_page(url))
    print("========== result in main==============")
    print(result_content)

    print("========== writing to file==============")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result_content)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a website and get its markdown representation."
    )
    parser.add_argument("--url", "-u", help="The URL of the website to crawl.", required=True)
    parser.add_argument( "--output", "-o", default="output.md", help="Where to save the file (default: output.md).", 
    required=False)
    args = parser.parse_args()
    print(args)
    main(args.url, args.output)
