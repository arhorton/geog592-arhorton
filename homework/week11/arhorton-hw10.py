#!/usr/bin/env python
# coding: utf-8

# ### Anna Horton - Automated Atlas Homework
# ONYEN: arhorton <br>
# PID: 730664552

# importing packages as neccessary to ensure that all functionalities are loaded
print("Importing modules!")
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages 
import argparse

## making the code more general - having it accept two arguments
## one argument is required, the other is not but it has a default value
parser = argparse.ArgumentParser(
        description = "A program that makes an atlas with the different locations of nursing homes in each county in the state"
    )

# I specifically made this atlas using NC data, but the statefp parameter still makes sense
print("Adding arguments")
parser.add_argument("countyfp", help = "FP code of the county to make a page fors")
print("creating the countyfp variable")
parser.add_argument("--countyCRS", default = "6543", help = "The name of the state that is assigned")
print("creating the color of the county polygon") ## the -- makes it not required (I have to type that first)
args = parser.parse_args()
countyfp = args.countyfp
countyCRS = args.countyCRS ## have to assign the variables down here to make sure that they are printing in the overall script
## I changed the parameter to ensure that the user could input the CRS if needed, but also not if they don't want to and there would be a default of 6543

# getting the US census data
url_0 = "https://www2.census.gov/geo/tiger/GENZ2024/shp/" # url for census tiger data 
url_county = "cb_2024_us_county_500k.zip" # county level
url_state = "cb_2024_us_state_500k.zip" # state level 

counties = gpd.read_file(url_0+url_county)
nc_counties = counties.loc[counties["STATEFP"] == "37"].to_crs(epsg = countyCRS).copy()

# since all of my code down below is assigned with the county name, I am reassigning the variable to the county name so that I don't have to change it down below
match = nc_counties.loc[nc_counties["COUNTYFP"] == countyfp.zfill(3), "NAME"]
if match.empty:
    raise ValueError(f"No NC County has COUNTYFP {countyfp!r}")
county_name = match.iloc[0] 
print(county_name)

## importing my vector layer for my automated atlas
nursing_homes = gpd.read_file("Nursing_Homes.geojson")

## the columns that I likely need to keep are: id, name, county, fips, beds, geometry
nursing_homes = nursing_homes[["id", "name", "county", "fips", "beds", "exc_beds", "geometry"]]
nursing_homes = nursing_homes.to_crs(epsg = countyCRS) ## assigning the correct CRS with the variable above

## Claude helped me with this section, also keeping all of the counties together 
print("Creating a join!")
joined = gpd.sjoin(
    nursing_homes,
    nc_counties[["NAME", "geometry"]],
    how="left",
    predicate="within",
)

beds = joined.groupby("NAME").agg(
    nursing_homes=("beds", "size"),
    total_beds=("beds", "sum"),
)

counts = joined.groupby("NAME").size().rename("nursing_homes")

nc_counties = (
    nc_counties.merge(counts, on="NAME", how="left")
    .fillna({"nursing_homes": 0, "total_beds": 0})
    .sort_values("NAME")
    .reset_index(drop=True)
)

print("Making county and locator maps")
## this function pulls out the map of only the county
county = county_name
def county_map(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]
    selected.plot(ax=ax, edgecolor="black", facecolor="#7b9b90")
    ax.set_axis_off() ## turns off the axis on the page, as it frequently gets cluttered and is not actively displaying

## this code prints out the plot of the entire state of NC and highlights a specific county, whatever is passed as the parameter to the function originally
def locator_map(county, ax):
    selected = nc_counties[nc_counties["NAME"] == county]
    nc_counties.plot(ax=ax, edgecolor="gray", facecolor="white")
    selected.plot(ax=ax, edgecolor="black", facecolor="#7b9b90")
    ax.set_axis_off()

## putting them together - this will be a page of the atlas, at its most basic
fig, axes = plt.subplots(
    2, 1,
    figsize=(8, 10),
    gridspec_kw={"height_ratios": [3, 1]}
)

county_map(county_name, axes[0])
locator_map(county_name, axes[1])

plt.show()

## Moving the figures around so that I can add additional information on the sides of the page
fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 10),
    gridspec_kw={
        "height_ratios": [3, 1],
        "width_ratios": [2, 1]
    }
)

county_map(county_name, axes[0, 0])
locator_map(county_name, axes[1, 0])
axes[0, 0].set_title("Nursing Home Information")

for ax in axes.flat:
    ax.set_axis_off()

#Let's make the pages a bit more interesting 
fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 10),
    gridspec_kw={
        "height_ratios": [3, 1],
        "width_ratios": [2, 1]
    }
)

county_map(county_name, axes[0, 0])
locator_map(county_name, axes[1, 0])

axes[1, 1].set_title("Nursing home bed information")

for ax in axes.flat:
    ax.set_axis_off()


fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 10),
    gridspec_kw={
        "height_ratios": [3, 1],
        "width_ratios": [2, 1]
    }
)

county_map(county_name, axes[0, 0])
locator_map(county_name, axes[1, 0])
axes[1, 1].set_title("Nursing home bed information")

for ax in axes.flat:
    ax.set_axis_off()

fig.suptitle(county_name, fontsize=30)

print("About to start printing more information on the page")
## this is the code that will allow me to print out a little bit more about the county onto the atlas pages
def county_info(county, ax):
    selected = nc_counties.loc[nc_counties["NAME"] == county].iloc[0]
    total_homes = int(selected["nursing_homes"])

    ax.text(
        -.2, 0.8,
        f"There are a total of {total_homes} nursing home(s) in this county.",
        transform=ax.transAxes,
        fontsize=14,
        color="olivedrab",
        va="top"
    )

#Let's make out pages a bit more interesting 
fig, axes = plt.subplots(
    2, 2,
    figsize=(12, 10),
    gridspec_kw={
        "height_ratios": [2, 1],
        "width_ratios": [2, 1]
    }
)

county_map(county_name, axes[0, 0])
locator_map(county_name, axes[1, 0])
county_info(county_name,  axes[0,1])

for ax in axes.flat:
    ax.set_axis_off()

fig.suptitle(nc_counties["NAME"], fontsize=30)

#Let's make it nicer and prettier for the PDF
print("Just finished working with the page structure")
county = county_name

fig = plt.figure(figsize=(12, 8))
ax_county = fig.add_axes([0.00, 0.23, 0.55, 0.54])
ax_locator = fig.add_axes([0.05, 0.08, 0.25, 0.12])
ax_info = fig.add_axes([0.55, 0.35, 0.18, 0.25])

county_map(county, ax_county)
locator_map(county, ax_locator)
county_info(county, ax_info)

for ax in (ax_county, ax_locator, ax_info):
    ax.set_axis_off()

# Page heading
fig.text(
    0.05, 0.94,
    "NORTH CAROLINA / County Atlas",
    fontsize=10,
    color="olivedrab"
)

fig.text(
    0.05, 0.87,
    f"{county} County",
    fontsize=28,
    fontweight="bold"
)

fig.text(
    .05, .83,
    f"Nursing Home Numbers",
    fontsize = 20,
    fontweight = "bold"
)

# Footer
fig.text(
    0.05, 0.03,
    "Source: U.S. Census Bureau | NC OneMap Data on Nursing Homes",
    fontsize=9,
    color="gray"
)


plt.show()

#Let's make it a function
print("Making this a function")
def county_figure(county, pdf):

    fig = plt.figure(figsize=(12, 8))

    # [left, bottom, width, height] as fractions of the figure
    # Coded with Ai help
    ax_county = fig.add_axes([0.00, 0.23, 0.55, 0.54])
    ax_locator = fig.add_axes([0.05, 0.08, 0.25, 0.12])
    ax_info = fig.add_axes([0.55, 0.35, 0.18, 0.25])


    county_map(county, ax_county)
    locator_map(county, ax_locator)
    county_info(county, ax_info)

    for ax in (ax_county, ax_locator, ax_info):
        ax.set_axis_off()

    # Page heading
    fig.text(
        0.05, 0.94,
        "NORTH CAROLINA / County Atlas",
        fontsize=10,
        color="olivedrab"
    )

    fig.text(
        0.05, 0.87,
        f"{county} County",
        fontsize=28,
        fontweight="bold"
    )

    fig.text(
    .05, .83,
    f"Nursing Home Numbers",
    fontsize = 20,
    fontweight = "bold"
)

    # Footer
    fig.text(
        0.05, 0.03,
        "Source: U.S. Census Bureau | NC OneMap Data on Nursing Homes",
        fontsize=9,
        color="gray"
    )

    pdf.savefig(fig, dpi=50)
    plt.close(fig)


## code came from Claude, trying to diagnose the PDF loading issue
import time

def timed(label, fn, *args):
    t = time.time()
    fn(*args)
    print(f"{label}: {time.time() - t:.2f}s")

fig = plt.figure(figsize=(12, 8))
ax1 = fig.add_axes([0.05, 0.23, 0.55, 0.54])
ax2 = fig.add_axes([0.05, 0.08, 0.25, 0.12])
ax3 = fig.add_axes([0.65, 0.12, 0.30, 0.32])

timed("county_map", county_map, county_name, ax1)
timed("locator_map", locator_map, county_name, ax2)
timed("county_info", county_info, county_name, ax3)
plt.close(fig)

## code came from Claude, trying to diagnose the PDF loading issue
import time
from matplotlib.backends.backend_pdf import PdfPages

with PdfPages("test.pdf") as pdf:
    t = time.time()
    county_figure("Orange", pdf)
    print(f"full page: {time.time() - t:.2f}s")

nc_counties = nc_counties.sort_values("NAME").reset_index(drop=True) ## making the code go to alphabetical order

with PdfPages("NC_Counties_NursingHomes.pdf") as pdf:  #with #manages a resource and automatically cleans up when you finish using it.
    for county in nc_counties["NAME"]:
        county_figure(county, pdf)


# ## AI statement
# 1) I used Claude AI. 
# 2) I had to use Claude because my PDF export was taking over 10 minutes and exporting thousands of pages instead of 100 (and I'm not sure why). I then found out my spatial join had converted my file of 100 rows to over 1000, which was the issue. I asked it to help diagnose that issue and then help me fix my spatial join. I also had to ask it to help me with my loop - the issue was that it was only printing the number of nursing homes in the first county and not scaling for the remainder. During the refactoring section of this assignment, I used Claude to address the issue that I was having with my countyfp variable, the new variable that I created with the argparse argument when generalizing and refactoring my code.
# 3) I had coded the spatial join the PDF Pages method. However, both were incorrect, as I quickly found out, and Claude helped me to diagnose the issue (as seen from the diagnostic code blocks above) and fix the issue itself. It helped me to bring my counties layer back to 100 counties (after going from 1028 to 99 and back to 100), which solved my PDF loading issue. It helped me to use the code that the professor provided and switch it slightly to account for my purposes. For the second part of the assignment, my GeoDataFrames after the joins were completely empty and I wasn't sure why; my code was then breaking further down. I asked Claude to diagnose the issue, and I was able to reassign the countfp variable to a variable related to the county's name to make sure that the rest of my code, which depended on the name of the county, wouldn't break.
# 4) I changed the format of the spatial join to aggregate by the count of nursing homes in each of the counties with a merge parameter. I also wrote in code to ensure that the counties that didn't have any nursing homes would also be counted within the pages (as it had been dropping them earlier). These fixes helped the PDF print in just 15 seconds instead of the over 11 minutes it was previously taking. I adjusted the function to print out the number of nursing homes for each county and used the .iloc[] that was already in there to scale. I also created a new variable that assigned the countyfp to the county_name so that I could put that in the rest of my code and it would print the atlas with the county names when the FP number was input to the function.


