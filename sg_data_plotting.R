library(dplyr)
library(ggplot2)

data = read.csv("path to granule data")


# SG count per cell -------------------------------------------------------


plot_data = data %>% 
  select(label_cell, protein, time, treatment, field_view, SG_count_per_cell) %>% 
  group_by(protein, treatment, time) %>%
  summarise(SG_count_per_cell = mean(SG_count_per_cell))

plot_data$time_converted = plot_data$time * 30

ggplot() + 
  geom_line(data = plot_data, aes(x = time_converted, y = SG_count_per_cell, colour = treatment)) +
  theme_classic() + 
  labs(x = 'time (min)', y = 'Mean stress granule count per cell')
