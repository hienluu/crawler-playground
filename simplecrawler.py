import asyncio
import argparse
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
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

async def crawl_wiki_page(url: str, element_id: str):
    print("==========crawl_wiki_page==============")
    browser_config = BrowserConfig(headless=True, text_mode=True)  # Default browser configuration

    markdown_generator = DefaultMarkdownGenerator(
                        content_source="cleaned_html",                        
                        content_filter=PruningContentFilter(),
                        options={
                            "ignore_links": True,
                            "ignore_images": True,
                            "escape_html": False,
                            "skip_internal_links": True
                        }  # removes boilerplate
                    )
    
    run_config = CrawlerRunConfig(
        #target_elements=["bodyContent"],
        css_selector="#bodyContent",
        excluded_tags=['form', 'header', 'footer', 'nav'],
        markdown_generator=markdown_generator
    )

    print("==========run_config==============")
    print(run_config)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        crawl_result = await crawler.arun(
            url=url,
            config=run_config
        )
    
    print(f"==========result.success: {crawl_result.success} ==============")
    print(f"==========result.status_code: {crawl_result.status_code} ==============")

    if crawl_result.success:
        title = crawl_result.metadata.get("title", "No title found")
        print(f"The title of '{url}' is: {title}")
    else:
        print(f"Failed to crawl '{url}'.")

    if crawl_result.markdown.fit_markdown:
        return crawl_result.markdown.fit_markdown
    else:
        return crawl_result.markddown
    


async def crawl_page(url: str):
    print("==========crawl_page==============")
    browser_config = BrowserConfig(headless=True, text_mode=True)  # Default browser configuration
   

    raw_md_generator = DefaultMarkdownGenerator(
            content_source="fit_html",
            options={"ignore_links": True},          
         )
    
    print("==========raw_md_generator.content_source==============")
    print(raw_md_generator.content_source)

    
    print("==========raw_md_generator.options==============")
    print(raw_md_generator.options)
    
    run_config = CrawlerRunConfig(
        excluded_tags=['form', 'header', 'footer', 'nav', 'block-qconfooter'],
        markdown_generator=raw_md_generator
    )   # Default crawl run configuration

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

def is_wiki(url: str) -> bool:
    return "en.wikipedia.org" in url

def main(url: str, output_file: str):
    result_content = ""
    if (is_txt(url)):
        result_content = asyncio.run(crawl_llm(url))
    elif (is_wiki(url)):
        result_content = asyncio.run(crawl_wiki_page(url, "bodyContent"))
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
    parser.add_argument("--url", "-u", help="The URL of the website to crawl.")
    parser.add_argument( "--output", "-o", default="output.md", help="Where to save the file (default: output.md).", 
    required=False)
    args = parser.parse_args()
    print(args)
    main(args.url, args.output)
