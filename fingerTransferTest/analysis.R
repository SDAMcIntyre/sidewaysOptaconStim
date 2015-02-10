rm(list=ls())
source('functions.R')

dataFiles <- dir(path='./rawData/',pattern='\\.txt')

rawData <- c()
for (fileNo in 1:length(dataFiles)) {
  rawData <- rbind(rawData,
                   read_raw_data(dataFiles[fileNo]) #read_raw_data() from functions.R
  )
}

splitVars <- c('experiment','participant')

data <- ddply(rawData, splitVars, process_data) #process_data() from functions.R

library(ggplot2)
theme_set(theme_classic())

quartz()
ggplot(subset(data, nTrials > 4), aes(x=ISOI, y=pComp)) +geom_point(shape=4, size=3) +scale_x_continuous(breaks=unique(data$ISOI)) +labs(title='Stadard ISOI = 82ms, proximal; duration = 50ms; N reps = 20', y = 'Proportion comparison called more proximal', x = 'Comparison ISOI (ms), proximal')
ggsave('pilot1_sarah_unadapted.eps')
ggsave('pilot1_sarah_unadapted.pdf')
