# from querent.kg.rel_helperfunctions.fixed_relationships import FixedRelationshipExtractor  # Adjust the import according to your project structure

# def test_fixed_entity_extractor():
#     full_document_text = """1. Introduction
# The impact of climate change on glaciers of the world has been a topic of active concern
# in recent times (Syed et al. 2007; Bagla 2009; Cogley et al. 2010). While glacial melt is a
# major source of freshwater that contributes to global mean sea level rise (Meier et al. 2007;
# Jacob et al. 2012), decreasing glacial mass has an impact on the freshwater resources of
# some of the largest river basins in the world, including that of the Ganges (e.g. Kumar,
# Singh, and Sharma 2005; Mall et al. 2006; Immerzeel, van Beek, and Bierkens 2010;
# Kaser, Grosshauser, and Marzeion 2010). Fluctuations in the recession rate of glaciers dur-
# ing recent years have initiated widespread discussions, especially in the context of global
# warming and its effects (Dyurgerov and Meier 2005). Similar ice mass changes have also
# been reported in the Garhwal region of the Himalayas (Kulkarni et al. 2005; Bhambri,
# Bolch, and Chaujar 2011a, 2011b; Kulkarni et al. 2011; Bolch et al. 2012). However, the
# *Corresponding author. Email: tsyed.ismu@gmail.com
# © 2013 Taylor & FrancisDownloaded by [Tajdarul Syed] at 06:13 15 October 2013
# 8654
# P. Saraswat et al.
# status of the Gangotri glacier warrants further investigation, particularly in the context of
# climate change resulting in continuous retreat, negative mass balance, and early melting of
# seasonal snow cover (Negi et al. 2012).
# Glaciers cover about 40,800 km2 of the Himalayan and Karakoram mountain region,
# and are one of the main sources of water to some of the largest rivers in the world, including
# the Ganges, Brahmaputra, and Indus (Kulkarni et al. 2011; Bajracharya and Shrestha 2011;
# Bolch et al. 2012). Approximately 10% of the summer discharge of the Ganges is attributed
# to melt waters from glaciers (Barnett, Adam, and Letternmaier 2005; Jain, Agarwal, and
# Singh 2007; Immerzeel, van Beek, and Bierkens 2010; Bolch et al. 2012). Rapid depletion
# of glaciers has had adverse effects on the flow regime of major Himalayan rivers, and can
# even lead to catastrophic events such as glacial lake outbursts (Govindha 2010; Shrestha,
# Eriksson, and Mool 2010; Ashraf, Naz, and Roohi 2012) and consequent flooding in the
# upper reaches of these rivers, affecting the lives of millions of people residing in the Indo-
# Gangetic plains (Richardson and Reynolds 2000; Bolch et al. 2012).
# In spite of their hydrologic, climatic, and socioeconomic significance, opportunities for
# precise and continuous monitoring of the Himalayan glaciers are limited by logistical and
# terrain-induced difficulties. Observations of Earth’s surface using satellite data have proven
# to be very useful in such monitoring; recent developments in high-resolution image acqui-
# sition have facilitated more precise monitoring of glacier movement (Luckman, Quincey,
# and Bevan 2007; Kumar, Venkataraman, and Hogda 2011; Kumar et al. 2011). Further,
# satellite data enables a gross analysis of glacier mass budgets, overcoming some of the
# problems of accessibility and sustainability of long-term measurements, that can later be
# verified with ground-based surveys (Kumar et al. 2008). The potential of remote sensing
# for glacier mass balance and velocity mapping has been demonstrated with optical (e.g.
# Kääb 2005; Scherler, Leprince, and Strecker 2008), synthetic aperture radar (SAR) (e.g.
# Luckman, Quincey, and Bevan 2007), and thermal infrared sensors (e.g. Nakawo, Yabuki,
# and Sakai 1999), and elevation models (Bolch, Pieczonka, and Benn 2011), among others.
# Developments in deriving flow rates and monitoring Himalayan glacier retreat using optical
# images have been made by Kääb (2005). However, this approach is sometimes limited by
# weather, clouds, and shadows in areas of high relief.
# In a novel approach, the current study presents one of the most comprehensive assess-
# ments of the Gangotri glacier in recent times (2004–2011). The methodology entails the
# utilization of interferometric SAR (InSAR) coherence and sub-pixel offset tracking. While
# complementing most previous studies, the result presented here establishes the effective-
# ness of the techniques implemented to produce robust estimates of areal changes and glacier
# surface velocity in near real time. But, perhaps most importantly, this is one of the few stud-
# ies which has shown the melting trend of Gangotri glacier over a considerably continuous
# period during recent times (2004–2011).
# 2. Study area
# The Gangotri glacier is a valley-type glacier and one of the largest Himalayan glaciers
# located in Uttarkashi district of Uttarakhand, India (Figure 1). Extending between the lat-
# itudes 30◦ 43 22 N–30◦ 55 49 N and longitudes 79◦ 4 41 E–79◦ 16 34 E, Gangotri
# is the only major Himalayan glacier that flows towards the northwest. It spans a length
# of 30.2 km, its width varies between 0.20 and 2.35 km, and it thereby covers an area of
# about 86.32 km2 . While the average thickness of the Gangotri glacier is ∼200 m, its sur-
# face elevation varies from 4000 to 7000 m above mean sea level (Jain 2008). Gangotri has
# three main tributaries, namely the Raktvarna, the Chaturangi, and the Kirti, with lengthsInternational Journal of Remote Sensing
# 70° 0′ 00″ E 75° 0′ 00″ E 80° 0′ 00″ E 85° 0′ 00″ E 90° 0′ 00″ E
# 79º 5' E
# 440 km
# 79º 10' E
# Raktvarna
# 30° 55′ N
# 220
# 30° 55′ N
# 35° 0′ 00″ N
# 0
# 8655
# Chaturangi
# 30° 0′ 00″ N
# 30° 50′ N
# tri
# go
# an
# G
# 25° 0′ 00″ N
# 30° 50′ N
# Kirti
# Shivling
# Hills
# Bhagirathi
# Hills
# 20° 0′ 00″ N
# 79° 5′ E
# Downloaded by [Tajdarul Syed] at 06:13 15 October 2013
# 0
# 79° 10′ E
# 2
# 4
# 6
# km
# Figure 1. Location of the Gangotri glacier in the overall Indian perspective. Also shown is a mag-
# nified view of the study area using an ASTER image illustrating the locations of the Gangotri glacier
# and its tributaries (Kirti, Raktvarna, and Chaturangi). The figure also marks the locations of the
# Shivling and Bhagirathi hills.
# of 15.90, 22.45, and 11.05 km, respectively (Figure 1). Additionally, there are more than
# 18 small tributary glaciers of Gangotri and its tributaries. Gangotri and other glaciers in
# this region are mostly fed by the summer monsoon and partly by winter snow. Western
# disturbances cause heavy snowfall from December to March over this region (Thayyen and
# Gergan 2010). Generally, seasonal melting star
# """  

#     fixed_relationships = ["impact of", "resulting in"]  # Example relationships

#     extractor = FixedRelationshipExtractor(fixed_relationships)
#     result = extractor.find_relationship_sentences(full_document_text)
#     reduction_percentage = extractor.measure_reduction(full_document_text, result)

#     assert "impact of" in result
#     assert "resulting in" in result
