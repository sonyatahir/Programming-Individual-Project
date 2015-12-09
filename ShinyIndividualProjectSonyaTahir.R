library(shiny)
library(rworldmap)
library(plyr)

maleDf <- read.csv('male.csv', header=TRUE)
femaleDf <- read.csv('female.csv', header=TRUE)

allCountries = unique(maleDf$Country)
allCountries <- data.matrix(allCountries)
newrow = c("All")
allCountries = rbind(newrow,allCountries)

yearSub = femaleDf[order(femaleDf$Year),]
yearSub = unique(yearSub$Year)
year <- data.matrix(yearSub)


maleSub = aggregate(Count ~ Year, maleDf, sum)
maleSub <- subset(maleSub, select = Count)
maleSub = maleSub/1000000
maleSub <- data.matrix(maleSub)

femaleSub = aggregate(Count ~ Year, femaleDf, sum)
femaleSub <- subset(femaleSub, select = Count)
femaleSub = femaleSub/1000000
femaleSub <- data.matrix(femaleSub)



server <- function(input, output) {
  output$MaleMap <- renderPlot({
    #hist(rnorm(input$obs), col = 'darkgray', border = 'white')
    
    
    maleSubMap <- maleDf[maleDf$Year == input$yr, ]
    maleSubMap = aggregate(Count ~ Country, maleSubMap, sum)

    #create a map-shaped window
    #mapDevice('x11')
    #join to a coarse resolution map
    spdf <- joinCountryData2Map(maleSubMap, joinCode="NAME", nameJoinColumn="Country")
    mapCountryData(spdf, nameColumnToPlot="Count", catMethod="fixedWidth", mapTitle="Total Male Children Out of School")
    
  })
  
  output$FemaleMap <- renderPlot({
    #hist(rnorm(input$obs), col = 'darkgray', border = 'white')
    
    femaleSubMap <- femaleDf[femaleDf$Year == input$yr, ]
    femaleSubMap = aggregate(Count ~ Country, femaleSubMap, sum)
    
    #create a map-shaped window
    #mapDevice('x11')
    #join to a coarse resolution map
    spdf2 <- joinCountryData2Map(femaleSubMap, joinCode="NAME", nameJoinColumn="Country")
    mapCountryData(spdf2, nameColumnToPlot="Count", catMethod="fixedWidth", mapTitle="Total Female Children Out of School")
    
  })
  
  datasetInput <- reactive({
    maleSubT <- maleDf[maleDf$Year == input$yr, ]
    femaleSubT <- femaleDf[femaleDf$Year == input$yr, ]
    
    bothT = merge(maleSubT, femaleSubT, by.x = "Country", by.y = "Country")
    bothT <- bothT[order(-(bothT$Count.x+bothT$Count.y)),] 
    bothT <- bothT[1:10,]
    bothT <- subset(bothT, select = (c("Country","Count.x","Count.y")))
    names(bothT)[2] <- "Counts (Male)"
    names(bothT)[3] <- "Counts (Female)"
    
    return(bothT) 
  })
  
  
  
  output$Table = renderTable({
    datasetInput()
  },include.rownames=FALSE)

  
  
  output$MalePlot <- renderPlot({
    if(input$ctry == "All")
    {
      plot(year, maleSub, type="o", col="red", ylab="Count (Millions)", xlab="Year")
      title(main='Total Male Children Out of School 2000-2015')
      mtext("All Countries")
    }
    else
    {
      maleSubCtry <- maleDf[maleDf$Country == input$ctry, ]
      maleSubCtry = aggregate(Count ~ Year, maleSubCtry, sum)
      maleSubCtry <- subset(maleSubCtry, select = Count)
      maleSubCtry = maleSubCtry/1000
      maleSubCtry <- data.matrix(maleSubCtry)

      plot(year, maleSubCtry, type="o", col="red", ylab="Count (Thousands)", xlab="Year")
      title(main='Total Male Children Out of School 2000-2015')
      mtext(input$ctry)
    }
    
  })
  
  output$FemalePlot <- renderPlot({
    if(input$ctry == "All")
    {
      plot(year, femaleSub, type="o", col="red", ylab="Count (Millions)", xlab="Year")
      title(main='Total Female Children Out of School 2000-2015')
      mtext("All Countries")
      
    }
    else
    {
      femaleSubCtry <- femaleDf[femaleDf$Country == input$ctry, ]
      femaleSubCtry = aggregate(Count ~ Year, femaleSubCtry, sum)
      femaleSubCtry <- subset(femaleSubCtry, select = Count)
      femaleSubCtry = femaleSubCtry/1000
      femaleSubCtry <- data.matrix(femaleSubCtry)
      
      plot(year, femaleSubCtry, type="o", col="red", ylab="Count (Thousands)", xlab="Year")
      title(main='Total Female Children Out of School 2000-2015')
      mtext(input$ctry)
    }
  })
  
  
}

ui <- shinyUI(fluidPage(
  sidebarLayout(
    sidebarPanel(
      sliderInput("yr", "Year", min = 2000, max = 2015, value = 1),
      selectInput("ctry", "Country", allCountries, selected = "All", multiple = FALSE, selectize = TRUE, width = NULL, size = NULL)
    ),
    mainPanel(
      tableOutput("Table"),
      plotOutput("MaleMap"),
      plotOutput("FemaleMap"),
      plotOutput("MalePlot", height="400px"),
      plotOutput("FemalePlot", height="400px")
  )
)))

shinyApp(ui = ui, server = server)

