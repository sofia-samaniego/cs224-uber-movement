library(rgeos)
library(rgdal)
library(igraph)

main_path <- "/Users/jvrsgsty/Documents/Stanford/ICME/CS224W/project/data/"
cities <- c("bogota/bogota_cadastral",
            "boston/boston_censustracts",
            #"boston/boston_taz",
            "johannesburg/johannesburg_gpzones",
            "manila/manila_hexes",
            "paris/paris_communes",
            "paris/paris_iris",
            "sydney/sydney_miz",
            "sydney/sydney_tz",
            "washington/washington_DC_censustracts",
            "washington/washington_DC_taz")

for (i in 1:length(cities)){
  filename <- paste(main_path, cities[i], sep="")
  polys <- readOGR(paste(filename,"json", sep="."), "OGRGeoJSON")
  m <- gTouches(polys, byid=TRUE)
  g <- graph.adjacency(m)
  G <- get.edgelist(g)
  # Offset the ids by 1 to make them correspond to Uber Ids
  ones <- matrix(1, nrow(G), ncol(G))
  GG <- as.numeric(G) + ones
  # Save the file
  write.table(GG, paste(filename,"csv", sep="."), row.names = FALSE, col.names= FALSE, sep=",")
}

