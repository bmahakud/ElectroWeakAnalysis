import FWCore.ParameterSet.Config as cms

from ElectroWeakAnalysis.VPlusJets.AllPassFilter_cfi import AllPassFilter
#from ElectroWeakAnalysis.VPlusJets.LooseLeptonVetoPAT_cfi import *



def WmunuCollectionsPAT(process,
                        patMuonCollection,
                        isQCD,
                        isHEEPID,
                        pTCutValue,
                        isTransverseMassCut,
                        TransverseMassCutValue,
                        patTypeICorrectedMet):




 isMuonAnalyzer = True

 print "                                      "
 print "######################################"
 print "## Muon Selection in W->munu events ##"
 print "######################################"
 print "                                      "

 print "Chosen Options:                      " 
 print "input pat muon collection                           = %s"%patMuonCollection
 print "is running QCD isolation cut                        = %d"%isQCD
 print "run the High pT muon ID instead of Tight  Muon ID   = %d"%isHEEPID
 print "chone pT thresold for the ID                        = %f"%pTCutValue
 print "apply tranverse mass cut                            = %d"%isTransverseMassCut
 print "transverse mass cut value                           = %f"%TransverseMassCutValue
 print "patTypeICorrectedMet                                = %s"%patTypeICorrectedMet
 print "                                      "
             

 isolationCutString = cms.string("")

 ### produce new muon  momentum using the new TuneP --> version of CMSSW after 5_3_5
 process.patTunePMuonPFlow = cms.EDProducer("TunePMuonProducer",
                                             mulabel = patMuonCollection)

 if isHEEPID:
    process.tightMuons = cms.EDFilter("PATMuonSelector",
                                       src = cms.InputTag("patTunePMuonPFlow"),
                                       cut = cms.string(""))

 else:
   process.tightMuons = cms.EDFilter("PATMuonSelector",
                                      src = cms.InputTag("patTunePMuonPFlow"),
                                      cut = cms.string(""))
         
 if isQCD:
    ### invert the isolation cut to select a QCD enriched sample in data 
    isolationCutString = "(pfIsolationR04().sumChargedHadronPt+max(0.,pfIsolationR04().sumNeutralHadronEt+pfIsolationR04().sumPhotonEt-0.5*pfIsolationR04().sumPUPt))/pt> 0.12" 

 else:
     if isHEEPID :
         ### Isolation Cut given by the Hight pT muon ID group
         isolationCutString = "trackIso()/pt< 0.1"
     else :
         isolationCutString = "(pfIsolationR04().sumChargedHadronPt+max(0.,pfIsolationR04().sumNeutralHadronEt+pfIsolationR04().sumPhotonEt-0.5*pfIsolationR04().sumPUPt))/pt< 0.12"


 if isHEEPID : process.tightMuons.cut = cms.string((" isGlobalMuon && isTrackerMuon && pt() > %f && abs(dB) < 0.2 && globalTrack().hitPattern().numberOfValidPixelHits() >0 "
                                                    " && globalTrack().hitPattern().numberOfValidMuonHits() >0 && globalTrack().hitPattern().trackerLayersWithMeasurement() > 8 "
                                                    " && numberOfMatchedStations() > 1 && abs(eta)< 2.1 && ptError/pt<0.3"+ isolationCutString)%pTCutValue)

               
 else : process.tightMuons.cut = cms.string((" cktTrack.pt()>%f && isGlobalMuon && isPFMuon && abs(eta)<2.4 && globalTrack().normalizedChi2<10"
                                             " && globalTrack().hitPattern().numberOfValidMuonHits>0 && globalTrack().hitPattern().numberOfValidPixelHits>0 && numberOfMatchedStations>1"
                                             " && globalTrack().hitPattern().trackerLayersWithMeasurement>5 && " + isolationCutString)%pTCutValue)

 ## tight mu filter --> at least one tight muon
 process.tightMuonFilter = cms.EDFilter("PATCandViewCountFilter",
                                         minNumber = cms.uint32(1),
                                         maxNumber = cms.uint32(999999),
                                         src = cms.InputTag("tightMuons"))

 process.tightLeptonStep = AllPassFilter.clone()

 ## produce the leptonic W candidate from reco Objects --> tight muon and corrected met Type I
 process.WToMunu = cms.EDProducer("CandViewShallowCloneCombiner",
                                   decay = cms.string("tightMuons"+patTypeICorrectedMet[0]),
                                   cut = cms.string('daughter(0).pt >%f && daughter(1).pt >%f && sqrt(2*daughter(0).pt*daughter(1).pt*(1-cos(daughter(0).phi-'
                                                     'daughter(1).phi)))>0'%(pTCutValue,pTCutValue)), 
                                   checkCharge = cms.bool(False))

 if isTransverseMassCut : process.WToMunu.cut = cms.string(' daughter(0).pt >%f && daughter(1).pt >%f && sqrt(2*daughter(0).pt*daughter(1).pt*(1-cos(daughter(0).phi-'
                                                           ' daughter(1).phi)))>%f'%(pTCutValue,pTCutValue,TransverseMassCutValue))


 process.bestWmunu = cms.EDFilter("LargestPtCandViewSelector",
                                   maxNumber = cms.uint32(10),
                                   src = cms.InputTag("WToMunu"))

 process.bestWToLepnuStep = AllPassFilter.clone()
 
 ## --------- Loose Lepton Filters ----------

# LooseLeptonVetoPAT(process,isQCD, isHEEPID, isMuonAnalyzer)

 process.WSequence = cms.Sequence(process.patTunePMuonPFlow*
                                  process.tightMuons *
                                  process.tightMuonFilter *
                                  process.tightLeptonStep *
                                  process.WToMunu *
                                  process.bestWmunu *
                                  process.bestWToLepnuStep)

# process.WPath = cms.Sequence(process.WSequence*process.VetoSequence)
