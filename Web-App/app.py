import streamlit as st
import json
import urllib
# from streamlit_lottie import st_lottie

# import numpy as np
import pandas as pd
# import seaborn as sns
from PIL import Image
import re
import matplotlib.pyplot as plt
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

# function
job_title = []
job_company = []
job_location = []
job_image = []
job_date = []
job_describtion = []
job_tags = []
job_requirements = []


def get_job_data(_all):
    
    for i in range(len(_all)):
        url = _all[i]
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html')
        
        job_title.append(soup.find("h1").text.strip())
        cname = soup.find("a", attrs= {"class":"topcard__org-name-link"}).text.strip()
        job_company.append(cname)
        job_location.append(soup.find("span", attrs= {"class":"topcard__flavor topcard__flavor--bullet"}).text.strip())
        job_image.append(soup.find("img", attrs={"class": "sub-nav-cta__image"})["data-delayed-url"])
        job_date.append(soup.find("span", attrs= {"class":"posted-time-ago__text"}).text.strip())
        more = []
        m = soup.find_all("span", attrs={"class":"description__job-criteria-text description__job-criteria-text--criteria"})
        for e in m:
            more.append(e.text.strip())
        more = list(set(more))
        job_tags.append(more)
        requirements_ = []
        requires = soup.find("div", attrs={"class":"show-more-less-html__markup"}).find_all("li")
        for li in requires:
            requirements_.append(li.text.strip())
        requirements_ = list(set(requirements_))
        
        job_requirements.append(requirements_)
        about = soup.find("div", attrs={"class":"show-more-less-html__markup"}).get_text(separator="\n ").split("\n")
        about = [i.strip() for i in about]
        about = [i for i in about if i]
        about = [i for i in about if not ( i.startswith("About") or i.startswith("#") )]
        about = list(set(about))
        job_describtion.append(about)
        time.sleep(50+random.random()*10)

    return pd.DataFrame({"Company": job_company, "Job Title": job_title, "Job Location":job_location, "Job Date": job_date, "Job Image URL": job_image, "Describtion": job_describtion, "Tags": job_tags, "Requirements": job_requirements})

def get_data(job):
    url = "https://www.linkedin.com/jobs/search/?keywords=" + job

    links = []
    for i in range(0, 125, 25):
        time.sleep(20+random.random()*10)
        html = urlopen(url+"&start="+str(i))
        soup = BeautifulSoup(html, 'html')

        job_results = soup.find("ul", attrs={"class":"jobs-search__results-list"}).find_all("li")
        
        for job in job_results:
            links.append(job.find("a", attrs={"class":"base-card__full-link"}))
    navs = pd.read_csv("csv/usstatesloc.csv", sep=',', encoding='utf-8')
    urls = []
    for link in links:
        try:
            urls.append(link["href"])
        except:
            urls.append("")
    urls = [i for i in urls if i]
    urls = list(set(urls))
    data = get_job_data(urls)
    exp = []
    for a in data["Tags"]:
        exp.append(a[0])
    data["Job Level"] = pd.Series(exp)
    ntags = []
    for a in data["Tags"]:
        ntags.append(a[1:])
    data["Tags"] = pd.Series(ntags)
    # data.drop("Unnamed: 0", axis = 1, inplace=True)
    locs = data['Job Location'].to_list()
    apv = []
    uns = ["New York, United States", "New York City Metropolitan Area", "San Francisco Bay Area", "Iowa, United States", "Texas, United States", "California, United States", "Dallas-Fort Worth Metroplex"]
    srt = ["NY", "NY", "NC", "IA", "TX", "CA", "TX"]
    for i in locs:
        if i == 'United States':
            apv.append("WA")
        else:
            try:
                apv.append(re.findall("([A-Z]{2})", i)[0])
            except:
                if i in uns:
                    apv.append(srt[uns.index(i)])
                else:
                    apv.append("WA")
    jlong = []
    jlati = []
    for i in apv:
        jlong.append(navs[navs["state"] == i]["longitude"].to_list()[0])
        jlati.append(navs[navs["state"] == i]["latitude"].to_list()[0])
    data["longitude"] = pd.Series(jlong)
    data["latitude"] = pd.Series(jlati)
    jco = []
    for i in data["Job Title"].to_list():
        jco.append(data['Job Title'].value_counts()[i])
    data['Count'] = pd.Series(jco)

    return data

# main configuration
st.set_page_config(page_title="LinkedIn Jobs", page_icon=":cyclone:", layout="wide")

# Header 
with st.container():
    st.title("Hi, I am Mohamed Salem :wave:")
    st.subheader("LinkedIn jobs")
    st.write("Search for a job and see analysis and detailed information about it and available opportunities in all companies.")

# More
with st.container():
    st.write("---")
    left_col, right_col = st.columns(2)
    with left_col:
        text_input = st.text_input(
        "Search for jobs now",
        key="placeholder")
    
    with right_col:
        image = Image.open('imgs/ms2.png')

        st.image(image, use_column_width="auto", width = 400)

with st.container():
    st.write("---")
    st.subheader("Analysis")
    if text_input:
        st.write("Your results for: ", text_input)
        df = get_data(urllib.parse.quote(text_input))
        st.dataframe(df)
        left_col, right_col = st.columns(2)
        with left_col:
            map = plt.figure(figsize=(12, 9))
            img = Image.open('geopandas-usa.png')
            plt.imshow(img,zorder=0,extent=[-126,-64,23,52])
            ax = plt.gca()
            df.plot(x='longitude', y='latitude', kind='scatter', alpha=0.4, label='jobs', ax=ax,
                    c="Count",
                    cmap=plt.get_cmap('Dark2'), colorbar=True, 
                    zorder=5)
            plt.legend()
            st.pyplot(map)
        
        with right_col:
            fig = plt.figure(figsize=(12,8))
            sns.countplot(data=df, x= 'Job Level', order=df['Job Level'].value_counts().index)
            st.pyplot(map)
