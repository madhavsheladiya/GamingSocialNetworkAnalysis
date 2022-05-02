library(jsonlite)
library(dplyr)
library(stringr)
library(tidyr)
library(tidyjson)
library(tidyverse)
library(igraph)

user_df <- read.csv(file = 'data/scraped_tweets.csv')

#remove users with no friends
sample <- subset(user_df, followers != "None")
#make a subset; we only need to retain data of users with some social activity
# sub <- subset(sample, year == 2005 & review_count >= 2 & no_of_friends >= 2)
sub <- subset(sample, retweetcount >= 2 & followers >= 2)
#make links (nodes and edges)
sample_friends <- sub %>% select(username, followers)
sample_users <- user_df[,5, drop=FALSE]
sample_dat <- data.frame(username = rep(sample_friends$username, sapply(sample_users, length)), friends = unlist(sample_users))
#network is still too big, take a random sample of 100k nodes
samp_net <- sample_n(sample_dat, 100)
#make network
network <- graph.data.frame(samp_net)
network_s <- simplify(network)
net_deg <- degree(network_s)
all_degree <- degree(network, mode = 'all')
#graph user with max degrees
sub_all <- subcomponent(network_s, which(all_degree == max(all_degree)), 'all')
g_sub <- induced_subgraph(network_s, sub_all)
#communities
graph.com <- fastgreedy.community(as.undirected(g_sub))
V(g_sub)$color <- graph.com$membership + 1
#create pdf graph for high resolution (try zooming in!)
pdf("data/communities2005.pdf", 10, 10)
plot(g_sub,
     vertex.color = V(g_sub)$color,
     vertex.size = 1,
     vertex.label = NA,
     vertex.frame.color = adjustcolor("#41424c", alpha.f = 0.25),
     edge.arrow.size = 0.1,
     edge.color = adjustcolor("#41424c", alpha.f = 0.20),
     edge.width = 1.5,
     edge.arrow.mode=0,
     layout=layout_with_lgl,
     asp = 0.9,
     dpi=300
)
dev.off()

#cliques/communities
cliques <- max_cliques(g_sub)
cliqueBP <- matrix(c(rep(paste0("cl", seq_along(cliques)), sapply(cliques, length)), names(unlist(cliques))), ncol=2, )
#shows which clique users belong to
bp <- graph_from_edgelist(cliqueBP, directed = F)
#to graph cliques, use the same code as above, but replace g_sub with bp
pdf("data/cliques2015.pdf", 10, 10)
plot(bp,
     vertex.size = all_degree,
     vertex.color = adjustcolor("lightgoldenrod3", alpha.f = 0.6),
     edge.color = adjustcolor("#41424c", alpha.f = 0.3),
     vertex.frame.color = adjustcolor("#41424c", alpha.f = 0.3),
     # vertex.label = ifelse(V(bp)$name %in% top_d1$user_id, top_d1$name, NA),
     vertex.label.color = "darkred",
     layout=layout_with_lgl,
     asp = 0.8,
     dpi = 300)
dev.off()