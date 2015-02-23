rm(list=ls())
source('functions.R')

dataFiles <- dir(path='./rawData/',pattern='\\.txt')

rawData <- c()
for (fileNo in 1:length(dataFiles)) {
  rawData <- rbind(rawData,
                   read_raw_data(dataFiles[fileNo]) #read_raw_data() from functions.R
  )
}

splitVars <- c('participant','condition','filename')

data <- ddply(rawData, splitVars, process_data) #process_data() from functions.R

library(ggplot2)
theme_set(theme_classic())

quartz()
ggplot(subset(data, nTrials > 4), aes(x=ISOI, y=pComp)) +geom_point(shape=4, size=3) +scale_x_continuous(breaks=unique(data$ISOI)) +scale_y_continuous(limits=c(0,1)) +labs(title='Stadard ISOI = 82ms, prox/dist; duration = 50ms; N reps = 20', y = 'Proportion comparison better direction signal', x = 'Comparison ISOI (ms), prox/dist matched to standard')
#ggsave('pilot_sarah_unadapted.eps')
#ggsave('pilot_sarah_unadapted.pdf')

ggplot(subset(data, nTrials > 0), aes(x=ISOI, y=pComp)) +geom_text(aes(label=nTrials), size=3) +facet_wrap(~filename, scales = 'free_x')  +scale_y_continuous(limits=c(0,1)) +stat_smooth(method = "glm", family = "binomial", se=F) +labs(title='Stadard ISOI = 82ms, prox/dist; duration = 50ms; numbers give N', y = 'Proportion comparison better direction signal', x = 'Comparison ISOI (ms), prox/dist, positive means matched to standard')
#ggsave('pilot_sarah_unadapted.eps')
#ggsave('pilot_sarah_unadapted.pdf')