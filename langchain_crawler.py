import argparse
import os
from urllib.parse import urlparse
from langchain_community.document_loaders import WikipediaLoader, WebBaseLoader, AsyncHtmlLoader
from langchain_community.document_transformers import MarkdownifyTransformer
from langchain_unstructured import UnstructuredLoader



def is_sitemap(url: str) -> bool:
    return url.endswith('sitemap.xml') or 'sitemap' in urlparse(url).path

def is_txt(url: str) -> bool:
    return url.endswith('.txt')

def is_wiki(url: str) -> bool:
    return "en.wikipedia.org" in url

def crawl_others_page(url: str, output_file: str):
    print(f">>>> crawl_others_page {url} and saving to {output_file}")
    #loader = WebBaseLoader(web_paths=[url])
    loader = UnstructuredLoader(web_url=url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
    )

    #md = MarkdownifyTransformer()
    #converted_docs = md.transform_documents(loader.load())

    documents = loader.load()
    print(f"===== len(documents): {len(documents)}")
    print(f"===== documents[0] metadata ====")
    print(f"{documents[0].metadata}\n")

    docs = []
    for doc in documents:
        #print(f"{doc.metadata}\n")        
        #docs.append(f"{doc.metadata['category']}: {doc.page_content}")
        docs.append(doc.page_content)

    
    doc = '\n'.join(docs)
    return doc

def crawl_others_page_in_md(url: str, output_file: str):
    print(f">>>> crawl_others_page_in_md {url} and saving to {output_file}")
    loader = WebBaseLoader(web_paths=[url])

    md = MarkdownifyTransformer()
    converted_docs = md.transform_documents(loader.load())

    print(f"===== metadata ====+")
    print(f"{converted_docs[0].metadata}\n")
    docs = []
    for doc in converted_docs:
        docs.append(doc.page_content)

    doc = ''.join(docs)
    return doc



def crawl_wiki_page(url: str, output_file: str):
    print(f"crawl_wiki_page {url} and saving to {output_file}")
    query = os.path.basename(url)
    print(f"query: {query}")

    
    docs = WikipediaLoader(query=query, load_max_docs=1, doc_content_chars_max=100000).load()
    print(f"length of docs: {len(docs)}")
    print(f"===== metadata ====")
    print(docs[0].metadata)
    return docs[0].page_content



def main(url: str, output_file: str):
    print(f"Crawling {url} and saving to {output_file}")
    if is_wiki(url):
        result_content = crawl_wiki_page(url, output_file)
    elif is_txt(url):
        result_content = crawl_others_page_in_md(url, output_file)
    else:
        result_content = crawl_others_page(url, output_file)

        
    print(f"===== result_content from main ====")
    print(result_content)

    
    if output_file != "no_output":
        print(f"===== writing result_content to file: {output_file}====")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result_content)
    else:
        print(f"===== not writing result_content to file ====")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl a website and get its markdown representation."
    )
    

    parser.add_argument("--url", "-u", help="url to retrieve content for", required=True)
    parser.add_argument( "--output", "-o", default="no_output", help="Where to save the file (default: output.md).", 
    required=False)
    args = parser.parse_args()
    print(args)
    main(args.url,  args.output)