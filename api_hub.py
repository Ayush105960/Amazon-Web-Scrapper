import requests
from flask_cors import cross_origin, CORS 
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pymongo
import logging
from flask import Flask , render_template , request , jsonify 
logging.basicConfig(filename= "Scrapper2.log")

app = Flask(__name__)

@app.route("/" , methods = ["GET"])
def home():
    return render_template("index.html")


@app.route("/review" , methods = ["POST" ,"GET"] )
def index():
    if request.method == 'POST' :
        try:    
            searchString = request.form['content'].replace(" " , "")
            amazon_url = "https://www.amazon.in/" + searchString
            print(amazon_url)
            amazon_html = urlopen(amazon_url)

            amazon_page = amazon_html.read()

            amazon_html.close()

            amazon_bs = bs(amazon_page , "html.parser")

            bigboxes = amazon_bs.find_all("div" , {"class" : "s-card-container s-overflow-hidden aok-relative puis-expand-height puis-include-content-margin puis s-latency-cf-section s-card-border"})

            product_link_list = []

            for each in bigboxes:
                product_link = "https://www.amazon.in" + each.div.div.div.span.a['href']
                product_link_list.append(product_link)

            product_link = product_link_list[5]
            product_link

            prodRes = requests.get(product_link)

            prodRes.encoding = "UTF-8"

            prod_html = bs(prodRes.text, "html.parser")

            product_details = prod_html.find("ul" , {"class" : "a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"})

            product_details_set = product_details.find_all("span" , {"class" : "a-list-item"})

            product_details_list = []
            for each in product_details_set:
                product_details_key = each.find("span" , {"class" : "a-text-bold"}).text.split("\n")[0]
                product_details_value = each.find("span" , {"class" : ""}).text
                product_details_list.append({product_details_key : product_details_value})


            commentsbox = prod_html.find("div" , {"class" : "a-section review-views celwidget"})

            commentsbox = commentsbox.find_all("div" , {"class" : "a-section review aok-relative"})

            result = []

            for each in commentsbox: 
                try:
                    comment = each.div.div.find("div" , {"class" : "a-row a-spacing-small review-data"}).span.div.div.span.text
                except :
                    logging.info("comment")
                    
                try:
                    cust_profile_link = "https://www.amazon.in" + commentsbox[0].div.div.div.a['href']
                except :
                    logging.info("Customer Profile Link")
                    
                try:
                    comment_heading = each.div.div.find_all("div" , {"class" : "a-row"})[1].span.text
                except :
                    logging.info("Comment heading")
                    
                try:
                    customer_name = each.div.div.find_all("div" , {"class" : "a-row"})[0].a.find("div" , {"class" : "a-profile-content"}).span.text
                except:
                    logging.info("customer name")
                    
                try:
                    purchase_type = each.div.div.find_all("div" , {"class" : "a-row"})[2].find_all("span" , {"data-hook" : "avp-badge-linkless"})[0].text
                except:
                    logging.info("Purchase Type")
                    
                try:
                    comment = each.div.div.find_all("div" , {"class" : "a-row"})[3].div.div.span.text
                except:
                    logging.info("Comment")
                    
                try:
                    comment_dt = each.div.div.find_all("span" , {"class" : "a-size-base a-color-secondary review-date"})[0].text.removeprefix("Reviewed in India 🇮🇳 on")
                except:
                    logging.info("Comment Date")
                    
                try:
                    rating = commentsbox[0].div.div.find_all("div" , {"class" : "a-row"})[1].a.span.text.removesuffix("out of 5 stars")
                except Exception as e:
                    print(e)
                mydict = {"Product" :  " " , "Name" : customer_name , "Rating" : rating , "Comment Heading" : comment_heading ,
                        "Comment" : comment , "Comment Date" : "comment_dt" , "Purchase Type" : purchase_type ,
                        "Custmer Profile Link " : cust_profile_link}
                result.append(mydict)
        
            return render_template("result.html" , reviews = result[: len(result)-1]) 
        except Exception as e:
            logging.info(e)
            return "something is wrong"
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0" , port= "8000" )