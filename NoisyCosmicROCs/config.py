pathToGlobus = "/data/users/cctrkdata/current/auth/proxy/"
userCertInGlobus = "proxy.cert"
userKeyInGlobus = "proxy.cert"
httpsMainDir = "https://cmsweb.cern.ch/dqm/online/data/browse/Original/"
tmpFileName = "remoteCopy.root"

pixelThreshold = 10000 #threshold on the number of digis per pixel to be considered noisy

clusterThreshold = 100 #threshold on the central pixel digis to search for a cluster around it
pixelsInClusterThreshold = 3 #minimum number of adjuacent pixels above threshold 

scatteredClusterThreshold = 20 #pixel threshold to search for extended noisy regions (spray)
scatteredClusterRadius = 12 # pixel over threshold are summed up on a square of RadiusXRadius
scatteredClusterNumberThreshold = 10 #threshold on the fraction of noisy scattered pixels over the total

outputDir = "OUT"
