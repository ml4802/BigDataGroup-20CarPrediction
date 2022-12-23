library(ggplot2)

# This takes the raw kaggle dataset and turns it into two files
# data_with_income.csv is the data we use, just not one-hotted
# one_hotted_training_data.csv is the data we use for training


# Vehicles.csv is the original document from Craigslist Kaggle
# It is around 1.5 Gb, place in the same folder as this file
master_data = read.csv("vehicles.csv")

# Keep the correct columns
master_nan = master_data[c('region','price','year','manufacturer', 'model', 'condition', 'cylinders', 'fuel', 'odometer', 'transmission', 'drive', 'size', 'type', 'paint_color', 'state', 'posting_date' )]
master_nan = na.omit(master_nan)

# Removes empty strings since the Kaggle database was dirty
master_nan = master_nan[master_nan$drive != "", ]
master_nan = master_nan[master_nan$cylinders != "", ]
master_nan = master_nan[master_nan$size != "", ]
master_nan = master_nan[master_nan$condition != "", ]
master_nan = master_nan[master_nan$paint_color != "", ]
master_nan = master_nan[master_nan$state != "", ]

# This part attatches the correct state income to each data point
income = read.csv("state_income.csv")
master_nan$state = toupper(master_nan$state)
master_nan$income_that_year = 0
master_nan$posting_date = strtoi(substr(master_nan$posting_date, 1, 4))

# Alaska and Hawaii are specially named, rename
income$GeoName[income$GeoName == "Alaska *"] = "Alaska"
income$GeoName[income$GeoName == "Hawaii *"] = "Hawaii"
state.abb
state.name

# A function to convert state name to abbreviation (from usdata r package)
statename_to_abbreviation <- function(state){
  ab <- tolower(c("AL",
                  "AK", "AZ", "KS", "UT", "CO", "CT",
                  "DE", "FL", "GA", "HI", "ID", "IL",
                  "IN", "IA", "AR", "KY", "LA", "ME",
                  "MD", "MA", "MI", "MN", "MS", "MO",
                  "MT", "NE", "NV", "NH", "NJ", "NM",
                  "NY", "NC", "ND", "OH", "OK", "OR",
                  "PA", "RI", "SC", "SD", "TN", "TX",
                  "CA", "VT", "VA", "WA", "WV", "WI",
                  "WY", "DC"))
  st <- tolower(c("Alabama",
                  "Alaska56789", "Arizona", "Kansas",
                  "Utah", "Colorado", "Connecticut",
                  "Delaware", "Florida", "Georgia",
                  "Hawaii", "Idaho", "Illinois",
                  "Indiana", "Iowa", "9899Arkansas",
                  "Kentucky", "Louisiana", "Maine",
                  "Maryland", "Massachusetts", "Michigan",
                  "Minnesota", "Mississippi", "Missouri",
                  "Montana", "Nebraska", "Nevada",
                  "New Hampshire", "New Jersey", "New Mexico",
                  "New York", "North123498 Carolina",
                  "North123498 Dakota1234",
                  "Ohio", "Oklahoma", "Oregon",
                  "Pennsylvania", "Rhode Island", "South Carolina",
                  "South Dakota1234", "Tennessee", "Texas",
                  "California", "Vermont", "Virginia",
                  "Washington", "West Virginia", "Wisconsin",
                  "Wyoming", "District of Columbia"))
  
  state <- tolower(as.character(state))
  state <- gsub("north", "north123498", state)
  state <- gsub("dakota", "dakota1234", state)
  state <- gsub("arkansas", "9899arkansas", state)
  state <- gsub("alaska", "alaska56789", state)
  ST    <- rep(NA, length(state))
  for (i in 1:length(st)) {
    ST[agrep(st[i], state, 0.2)] <- i
  }
  toupper(ab[ST])
}

# Attatch the income of the state from 2021 to each row entry
income$GeoName = statename_to_abbreviation(income$GeoName)
year2021 = income$X2021
master_nan$income_this_year = year2021[match(master_nan$state, state.abb)+1]

# Removes weird leftover column
master_nan = subset(master_nan, select = -c(income_that_year) )

# This data is not one-hotted, used for analysis
write.csv(master_nan,file='data_with_income.csv', row.names=FALSE)

# This part generates the one-hotted version of the data for training
library(caret)
library(dplyr)
master_data = master_nan
no_nans = master_data[master_data$price > 0, ]

# Instead of removing rows with missing elements, we just mark them as "other"
no_nans$manufacturer[no_nans$manufacturer == "" ] <- "other"
no_nans$type[no_nans$type == ""] <- "other"
no_nans$transmission[no_nans$transmission == ""] <- "other"
no_nans <- na.omit(no_nans)

# We remove cars we found did not have large numbers of representations
# This saves space while one-hotting and leads to a better model overall after training
no_nans$manufacturer[no_nans$manufacturer == "aston-martin"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "datsun"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "alfa-romeo"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "tesla"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "harley-davidson"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "fiat"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "jaguar"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "porsche"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "saturn"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "rover"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "mercury"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "mini"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "mitsubishi"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "volvo"] = "other"
no_nans$manufacturer[no_nans$manufacturer == "infiniti"] = "other"

# Prints unique number of manufacturers
unique(no_nans$manufacturer)

# Removes obscure categories of cylinders
no_nans = subset(no_nans, no_nans$cylinders != c("10 cylinders", "5 cylinders", "3 cylinders", "12 cylinders", "other"), )
unique(no_nans$cylinders)

# Consolidates obscure categories of vehicles
no_nans$type[no_nans$type == "bus"] = "other"
no_nans$type[no_nans$type == "offroad"] = "other"
no_nans$type[no_nans$type == "wagon"] = "other"
no_nans$type[no_nans$type == "mini-van"] = "van"

# Consodlidates obscure catgeories of paint colors
no_nans$paint_color[no_nans$paint_color == "green"] = "other"
no_nans$paint_color[no_nans$paint_color == "brown"] = "other"
no_nans$paint_color[no_nans$paint_color == "custom"] = "other"
no_nans$paint_color[no_nans$paint_color == "yellow"] = "other"
no_nans$paint_color[no_nans$paint_color == "purple"] = "other"
no_nans$paint_color[no_nans$paint_color == "orange"] = "other"

# Gives a numerical ranking of quality of the car for training
no_nans$condition[no_nans$condition == "excellent"] = 10
no_nans$condition[no_nans$condition == "like new"] = 15
no_nans$condition[no_nans$condition == "good"] = 6
no_nans$condition[no_nans$condition == "fair"] = 3
no_nans$condition[no_nans$condition == "new"] = 20
no_nans$condition[no_nans$condition == "salvage"] = 0
no_nans$condition = as.numeric(no_nans$condition)

# Renames the cylinders to numerical values rather than string
no_nans$cylinders[no_nans$cylinders == "6 cylinders"] = 6
no_nans$cylinders[no_nans$cylinders == "4 cylinders"] = 4
no_nans$cylinders[no_nans$cylinders == "8 cylinders"] = 8
no_nans$cylinders = as.numeric(no_nans$cylinders)

# THis is where one-hotting occurs on all categorical variables
df = no_nans

dummy <- dummyVars(" ~ manufacturer", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

dummy <- dummyVars(" ~ fuel", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

dummy <- dummyVars(" ~ transmission", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

dummy <- dummyVars(" ~ drive", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

dummy <- dummyVars(" ~ size", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

dummy <- dummyVars(" ~ type", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

dummy <- dummyVars(" ~ paint_color", data=df)
final_df <- data.frame(predict(dummy, newdata=df))
no_nans = cbind(no_nans, final_df)

# Removing the original categorial categories after adding the new one-hotted versions
no_nans$manufacturer <- NULL
no_nans$fuel <- NULL
no_nans$transmission <- NULL
no_nans$drive <- NULL
no_nans$size <- NULL
no_nans$type <- NULL
no_nans$paint_color <- NULL
no_nans$drive <- NULL

no_nans$region <- NULL
no_nans$model <- NULL
no_nans$state <- NULL

no_nans = no_nans %>% distinct()
no_nans = na.omit(no_nans)

# This file can be directly used in the training of machine learning models
write.csv(no_nans, "one_hotted_training_data.csv", row.names=FALSE)



