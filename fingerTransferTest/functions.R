library(stringr); library(plyr)

read_raw_data <- function(fname, keepFileName = TRUE) {
  # This function reads in the raw data from a file to a data frame. It also adds 
  # codes returned from validate_data() to the data frame as extra columns. These codes 
  # indicate the experiment, participant, and experimental conditions.
  
  condValues <- strsplit( strsplit(fname,'\\.')[[1]][1], '_' )[[1]]
  
  readData <- read.table(file=paste0('./rawData/',fname), header = TRUE)
  
  output <- data.frame(experiment = condValues[1],
                       participant = condValues[2],
                       condition = condValues[3],
                       readData,
                       filename = fname)
  if (keepFileName) {
    return(output) } else {
      return(subset(output,select=-filename)) 
    }
}

process_data <- function(raw)  {
  # This function takes the raw responses to each trial and
  # returns a data frame with the proportion of responses for
  # each comparison frequency. This is necessary for fitting
  # a psychometric function.
  
  count_responses <- function(df) {
    nComp <- sum(df$response)
    nTrials <- length(df$response)
    pComp <- nComp/nTrials
    data.frame(nComp,nTrials,pComp)
  }
  
  ddply(raw, .(ISOI), count_responses)
  
}

correct_floor_ceil <- function (df,displayWarnings=TRUE) {  
  # This function is used to adjust floor (0) and ceiling (1) proportion values 
  # so they can be used for fitting a logistic regression function. qlogis() returns
  # NA to 0 and 1 values. 0 is adjusted up and 1 is adjusted down, by a value 
  # corresponding to half a trial. For example, if there were 10 trials, the value 
  # would be adjusted by adding or subtracting 0.05 (because 1 trial corresponds to 0.1).
  #
  # If multiple values are at floor or ceiling, the more extreme values are converted
  # to NA so they will be ignored for curve fitting.
  
  compFreqC = df$compFreq - mean(df$compFreq)
  if (cor(df$compFreq,df$pFaster) < 0) compFreqC = -compFreqC # correct if button presses were reversed
  df$pFaster_adj <- df$pFaster
  
  fl = df$pFaster == 0 # if multiple floor responses, lowest are made NA
  while (sum(fl) > 1) {
    minFloor <- compFreqC*fl == min(compFreqC*fl)
    df$pFaster_adj[minFloor] = NA
    fl[minFloor]= FALSE
    if (displayWarnings) warning(paste0('Multiple comparisons at floor. Data for ',df$compFreq[minFloor],'Hz will be ignored for fitting psychometric function.'))
  }
  
  cl = df$pFaster == 1 # if multiple ceiling responses, highest are made NA
  while (sum(cl) > 1) {
    maxCeil <- compFreqC*cl == max(compFreqC*cl)
    df$pFaster_adj[maxCeil] = NA
    cl[maxCeil] = FALSE
    if (displayWarnings) warning(paste0('Multiple comparisons at ceiling. Data for ',df$compFreq[maxCeil],'Hz will be ignored for fitting psychometric function.'))
  }
  
  if (sum(fl) > 0) {
    df$pFaster_adj[fl] = 1/(df$nTrials[fl]*2)
    if (displayWarnings) warning(paste0('Data for ',df$compFreq[fl],'Hz at floor, has been adjusted to: ',df$pFaster_adj[fl]))
  }
  
  if (sum(cl) > 0 ) {
    df$pFaster_adj[cl] = (df$nTrials[cl]*2-1)/(df$nTrials[cl]*2)
    if (displayWarnings) warning(paste0('Data for ',df$compFreq[cl],'Hz at ceiling, has been adjusted to: ',df$pFaster_adj[cl]))
  }
  return(df)
}

fit_logistic_curve <- function(df,get = c('fullData','summaryData','plotData'),...) {
  # This function fits a logistic regression function to the data. First, floor and
  # ceiling data are a djusted, then a logit transformation is applied, and a line
  # fitted to the transformed data.
  #
  # Three data frame can be returned (according to 'get' parameter).
  
  # fullData:
  # the input data frame with ceiling/floor corrected values added as a column
  
  # summaryData:
  # slope and intercept of the line
  # PSE (point of subject equality), the value of the comparison frequency at 
  # half-way point on the line, indicating perceived frequency of the standard
  # Weber fraction: an indication of discrimination sensitivity
  
  # plotData:
  # a data frame with 200 points for corresponding comparison frequencies and
  # and proportions (converted back to original units) that can be used for
  # plotting the psychometric functions.
  
  
  # adjust for floor and ceiling responses
  df <- correct_floor_ceil(df=df,...)
  
  #logit transform the data
  df$pFaster_logit <- qlogis(df$pFaster_adj)  
  
  #fit linear regression, calculate PSE & slope
  linearfit <- lm(pFaster_logit ~ compFreq, df)
  slope <- linearfit$coefficients[2]; names(slope) <- NULL
  intercept <- linearfit$coefficients[1]; names(intercept) <- NULL
  pse <- -intercept/slope
  
  #calculate Weber fraction
  thresh75 = (qlogis(0.75)-intercept) / slope
  weber = (thresh75-pse)/pse
  
  # points for plotting a line
  x <- seq(min(df$compFreq),max(df$compFreq),length.out=200)
  y <- plogis(intercept + slope*x)
  
  output <- list(
    fullData=df,
    summaryData = data.frame(intercept=intercept,slope=slope,pse=pse,weber=weber), 
    plotData = data.frame(compFreq = x, pFaster = y))
  
  if (length(get) == 1) {
    return(output[get][[1]]) } else {
      return(output[get])
    }
  
}