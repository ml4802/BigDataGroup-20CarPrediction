library(caret)
library(dplyr)
master_data = read.csv("with_income.csv")
master_data
no_nans = master_data[master_data$price > 0, ]
no_nans$manufacturer[no_nans$manufacturer == "" ] <- "other"
no_nans$type[no_nans$type == ""] <- "other"
no_nans$transmission[no_nans$transmission == ""] <- "other"
no_nans <- na.omit(no_nans)

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

unique(no_nans$manufacturer)

no_nans = subset(no_nans, no_nans$cylinders != c("10 cylinders", "5 cylinders", "3 cylinders", "12 cylinders", "other"), )

unique(no_nans$cylinders)

no_nans$type[no_nans$type == "bus"] = "other"
no_nans$type[no_nans$type == "offroad"] = "other"
no_nans$type[no_nans$type == "wagon"] = "other"
no_nans$type[no_nans$type == "mini-van"] = "van"

no_nans$paint_color[no_nans$paint_color == "green"] = "other"
no_nans$paint_color[no_nans$paint_color == "brown"] = "other"
no_nans$paint_color[no_nans$paint_color == "custom"] = "other"
no_nans$paint_color[no_nans$paint_color == "yellow"] = "other"
no_nans$paint_color[no_nans$paint_color == "purple"] = "other"
no_nans$paint_color[no_nans$paint_color == "orange"] = "other"

no_nans$condition[no_nans$condition == "excellent"] = 10
no_nans$condition[no_nans$condition == "like new"] = 15
no_nans$condition[no_nans$condition == "good"] = 6
no_nans$condition[no_nans$condition == "fair"] = 3
no_nans$condition[no_nans$condition == "new"] = 20
no_nans$condition[no_nans$condition == "salvage"] = 0
no_nans$condition = as.numeric(no_nans$condition)

no_nans$cylinders[no_nans$cylinders == "6 cylinders"] = 6
no_nans$cylinders[no_nans$cylinders == "4 cylinders"] = 4
no_nans$cylinders[no_nans$cylinders == "8 cylinders"] = 8
no_nans$cylinders = as.numeric(no_nans$cylinders)

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

write.csv(no_nans, "one_hotted.csv", row.names=FALSE)

unique(no_nans$manufacturer)

