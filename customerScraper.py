'''
Customer scraping: www.chorus.ai
--------------------------------
As not all customers are available on a single page(without a JS action), the 
individual category pages are scraped and then combined into a single output file.
The featured customer on the customer overview page is extracted separately.

This solution works as is, but makes a few assumptions for simplicity's sake:
  - Every customer has their own card with a logo in the grid
  - Every customer has a separate case study page
  - Every customer belongs to a category

The customers' domain names are accessible only on their respective case study pages.
Extracting the domain name is therefore done by requesting the full case study page for each of the customers. 
Code runtime and cleanliness could be improved by outputting the URLs to each case study instead of the actual customer domains.

Customer duplicates are not being removed as some customers have multiple different case studies.
'''

import requests
import json
from bs4 import BeautifulSoup

LANDINGURL  = "https://www.chorus.ai/customers"
BASEURL     = "https://www.chorus.ai/case-studies/category/"
CATEGORIES  = ["productivity", "quota-attainment", "coaching", "customer-success"]
# HEADERS     = {"User-Agent": ""}

class Customer():
    def __init__(self, name, logoUrl, caseStudy, domain):
      self.name         = name
      self.logoUrl      = logoUrl
      self.caseStudy    = caseStudy
      self.domain       = domain

def main():
    # Customers on category pages
    categoryPages   = [ requestPage(BASEURL + c) for c in CATEGORIES ]
    customers       = [ c for page in categoryPages for c in scrape(page) ]
    # Featured customer on landing page
    landingPage         = requestPage(LANDINGURL)
    featuredCustomer    = scrapeFeaturedCustomer(landingPage)
    customers.append(featuredCustomer)
    # File output
    customersStr = json.dumps([c.__dict__ for c in customers], indent=4)
    with open("output.json", "w") as outfile:
        outfile.write(customersStr)

def scrape(page):
    soup            = BeautifulSoup(page.content, "html.parser")
    customerCards   = soup.find_all("a", attrs={"class": "card-post__logo"})
    customers       = []
    for customerCard in customerCards:
        logoUrl         = extractLogoUrl(customerCard)
        caseStudyUrl    = extractCaseStudyUrl(customerCard)
        
        caseStudyPage   = requestPage(caseStudyUrl)
        domain          = scrapeDomain(caseStudyPage)
        name            = scrapeName(caseStudyPage)

        customer = Customer(name, logoUrl, caseStudyUrl, domain)
        customers.append(customer)
    return customers

def requestPage(url):
    page = requests.get(url, headers=HEADERS)
    return page

def extractLogoUrl(customerCard):
    logoUrl = customerCard.img["src"]
    return logoUrl

def extractCaseStudyUrl(customerCard):
    caseStudyUrl = customerCard["href"]
    return caseStudyUrl

def scrapeName(caseStudyPage):
    soup            = BeautifulSoup(caseStudyPage.content, "html.parser")
    customerName    = soup.find_all("a", attrs={"class": "breadcrumb__link"})[1].get_text()
    return customerName

def scrapeDomain(caseStudyPage):
    soup            = BeautifulSoup(caseStudyPage.content, "html.parser")
    customerDomain  = soup.find("a", attrs={"class": "alt-btn__inner"})["href"]
    return customerDomain

def scrapeFeaturedCustomer(landingPage):
    soup                = BeautifulSoup(landingPage.content, "html.parser")
    featuredLogo        = soup.find("div", attrs={"class": "heading__logo"}).img["src"]
    featuredStudyUrl    = soup.find("a", attrs={"class": "featured-banner"})["href"]

    featuredPage        = requestPage(featuredStudyUrl)
    featuredName        = scrapeName(featuredPage)
    featuredDomain      = scrapeDomain(featuredPage)
    featuredCustomer    = Customer(featuredName, featuredLogo, featuredStudyUrl, featuredDomain)
    return featuredCustomer

if __name__ == "__main__":
    main()

