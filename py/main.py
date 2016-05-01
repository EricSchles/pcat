
# coding: utf-8

# In[127]:

from __init__ import *


# In[128]:

def retr_fwhm(psfn):
    
    fwhm = zeros((numbener, numbevtt))
    for i in indxener:
        for m in indxevtt:
            jangldisp = argsort(psfn[i, :, m])
            intpfwhm = max(amax(psfn[i, :, m]) / 2., amin(psfn[i, :, m]))
            if intpfwhm > amin(psfn[i, jangldisp, m]) and intpfwhm < amax(psfn[i, jangldisp, m]):
                fwhm[i, m] = 2. * interp1d(psfn[i, jangldisp, m], angldisp[jangldisp])(intpfwhm) # [rad]
    return fwhm


# In[129]:

def retr_spec(flux, sind):

    if isscalar(flux):
        flux = array([flux])

    if isscalar(sind):
        sind = array([sind])
        
    spec = flux[None, :] * (meanener[:, None] / enerfdfn)**(-sind[None, :])
    
    return spec


# In[130]:

def retr_indx(indxpntsfull):    

    indxsamplgal = []
    indxsampbgal = []
    indxsampspec = []
    indxsampsind = []
    indxsampcomp = []
    for l in indxpopl:
        indxsamplgaltemp = indxcompinit + maxmnumbcomp * l + array(indxpntsfull[l], dtype=int) * numbcomp
        indxsamplgal.append(indxsamplgaltemp)
        indxsampbgal.append(indxsamplgaltemp + 1)
        indxsampspec.append(repeat((indxsamplgaltemp + 2)[None, :], numbener, 0) +                          repeat(arange(numbener), len(indxpntsfull[l])).reshape(numbener, -1))
        if colrprio:
            indxsampsind.append(indxsamplgaltemp + 2 + numbener)
        indxsampcomp.append(repeat(indxsamplgaltemp, numbcomp) + tile(arange(numbcomp, dtype=int), len(indxpntsfull[l])))

    return indxsamplgal, indxsampbgal, indxsampspec, indxsampsind, indxsampcomp


# In[131]:

def retr_pntsflux(lgal, bgal, spec, psfipara):
    
    numbpnts = lgal.size
    
    dist = empty((npixl, numbpnts))
    for k in range(numbpnts):
        dist[:, k] = retr_dist(lgal[k], bgal[k], lgalgrid, bgalgrid)

    # convolve with the PSF
    pntsflux = empty((numbpnts, numbener, npixl, numbevtt))
    for k in range(numbpnts):
        psfn = retr_psfn(psfipara, indxener, dist[:, k], psfntype=modlpsfntype)
        pntsflux[k, :, :, :] = spec[:, k, None, None] * psfn

    # sum contributions from all PS
    pntsfluxtemp = sum(pntsflux, 0) 
    


    return pntsfluxtemp


def retr_rofi_flux(normback, pntsflux, tempindx):


    modlflux = pntsflux[tempindx]
    for c in indxback:
        modlflux += normback[c, :, None, None] * backflux[c][tempindx]        
    
    
    return modlflux


# In[132]:

def cdfn_spec_brok(flux, fdfnsloplowr, fdfnslopuppr, fluxbrek, i):

    norm = 1. / ((1. - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr)) / (1. - fdfnsloplowr) +                  ((maxmspec[i] / fluxbrek)**(1. - fdfnslopuppr) - 1.) / (1. - fdfnslopuppr))

    if flux <= fluxbrek:
        
        fluxunit = norm / (1. - fdfnsloplowr) *             ((flux / fluxbrek)**(1. - fdfnsloplowr) - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr))
        
    else:
        
        fluxunit = norm / (1. - fdfnsloplowr) * (1. - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr)) -             norm / (1. - fdfnslopuppr) * (1. - (flux / fluxbrek)**(1. - fdfnslopuppr))
       
    return fluxunit


def pdfn_spec_brok(flux, fdfnsloplowr, fdfnslopuppr, fluxbrek, i):

    norm = 1. / ((1. - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr)) / (1. - fdfnsloplowr) +                  ((maxmspec[i] / fluxbrek)**(1. - fdfnslopuppr) - 1.) / (1. - fdfnslopuppr))

    if flux <= fluxbrek:
        
        pdfnflux = norm * (flux / fluxbrek)**(1. - fdfnsloplowr)
        
    else:
        
        pdfnflux = norm * (flux / fluxbrek)**(1. - fdfnslopuppr)
        
    return pdfnflux


def icdf_spec_brok(fluxunit, fdfnsloplowr, fdfnslopuppr, fluxbrek, i):
    
    norm = 1. / ((1. - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr)) / (1. - fdfnsloplowr) -                  (1. - (maxmspec[i] / fluxbrek)**(1. - fdfnslopuppr)) / (1. - fdfnslopuppr))
    
    fluxunitbrek = norm / (1. - fdfnsloplowr) * (1. - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr))
    
    if fluxunit < fluxunitbrek:
        
        flux = fluxbrek * (fluxunit * (1. - fdfnsloplowr) / norm +                        (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr))**(1. / (1. - fdfnsloplowr))
        
    else:
        
        flux = fluxbrek * (1. - (norm / (1. - fdfnsloplowr) * (1. - (minmspec[i] / fluxbrek)**(1. - fdfnsloplowr)) -                                  fluxunit) * (1. - fdfnslopuppr) / norm)**(1. / (1. - fdfnslopuppr))

    return flux


# In[133]:

def cdfn_spec(flux, fdfnslop, minmspectemp, maxmspectemp):
        
    fluxunit = (flux**(1. - fdfnslop) - minmspectemp**(1. - fdfnslop)) / (maxmspectemp**(1. - fdfnslop) - minmspectemp**(1. - fdfnslop))
        
    return fluxunit


def icdf_spec(fluxunit, fdfnslop, minmspectemp, maxmspectemp):
    
    flux = (fluxunit * (maxmspectemp**(1. - fdfnslop) - minmspectemp**(1. - fdfnslop)) + minmspectemp**(1. - fdfnslop))**(1. / (1. - fdfnslop))
    
    return flux


def pdfn_spec(flux, fdfnslop, minmspectemp, maxmspectemp):
  
    pdfnflux = (1. - fdfnslop) / (maxmspectemp**(1. - fdfnslop) - minmspectemp**(1. - fdfnslop)) * flux**(-fdfnslop)
          
    return pdfnflux


    
def icdf_self(paraunit, minmpara, factpara):
    para = factpara * paraunit + minmpara
    return para


def cdfn_self(para, minmpara, factpara):
    paraunit = (para - minmpara) / factpara
    return paraunit



def icdf_logt(paraunit, minmpara, factpara):
    para = minmpara * exp(paraunit * factpara)
    return para


def cdfn_logt(para, minmpara, factpara):
    paraunit = log(para / minmpara) / factpara
    return paraunit



def icdf_atan(paraunit, minmpara, factpara):
    para = tan(factpara * paraunit + arctan(minmpara))
    return para


def cdfn_atan(para, minmpara, factpara):
    paraunit = (arctan(para) - arctan(minmpara)) / factpara
    return paraunit




def icdf_psfipara(psfiparaunit, jpsfipara):
    
    if scalpsfipara[jpsfipara] == 'self':
        psfipara = icdf_self(psfiparaunit, minmpsfipara[jpsfipara], factpsfipara[jpsfipara])
    if scalpsfipara[jpsfipara] == 'logt':
        psfipara = icdf_logt(psfiparaunit, minmpsfipara[jpsfipara], factpsfipara[jpsfipara])
    if scalpsfipara[jpsfipara] == 'atan':
        psfipara = icdf_atan(psfiparaunit, minmpsfipara[jpsfipara], factpsfipara[jpsfipara])

    if False:
        print 'icdf_psfipara'
        print 'psfiparaunit'
        print psfiparaunit
        print 'jpsfipara'
        print jpsfipara
        print 'psfipara'
        print psfipara
        print 'minmpsfipara[jpsfipara]'
        print minmpsfipara[jpsfipara]
        print 'factpsfipara[jpsfipara]'
        print factpsfipara[jpsfipara]
        print
        print
        print

    
    return psfipara


def cdfn_psfipara(psfipara, jpsfipara):
    

    if scalpsfipara[jpsfipara] == 'self':
        psfiparaunit = cdfn_self(psfipara, minmpsfipara[jpsfipara], factpsfipara[jpsfipara])
    if scalpsfipara[jpsfipara] == 'logt':
        psfiparaunit = cdfn_logt(psfipara, minmpsfipara[jpsfipara], factpsfipara[jpsfipara])
    if scalpsfipara[jpsfipara] == 'atan':
        psfiparaunit = cdfn_atan(psfipara, minmpsfipara[jpsfipara], factpsfipara[jpsfipara])

    if False:
        print 'cdfn_psfipara'
        print 'psfipara'
        print psfipara
        print 'jpsfipara'
        print jpsfipara
        print 'psfiparaunit'
        print psfiparaunit
        print 'minmpsfipara[jpsfipara]'
        print minmpsfipara[jpsfipara]
        print 'maxmpsfipara[jpsfipara]'
        print maxmpsfipara[jpsfipara]
        print 'factpsfipara[jpsfipara]'
        print factpsfipara[jpsfipara]
        print 'scalpsfipara[jpsfipara]'
        print scalpsfipara[jpsfipara]
        print
        print
        print

    
    return psfiparaunit




# In[134]:

def retr_poisoffs_hist(norm, diffvarb, meanvarb, mean, offs):
    
    meanvarbtran = meanvarb + offs
    
    print 'meanvarbtran'
    print meanvarbtran
    print 
        
    return diffvarb * norm * exp(meanvarbtran * log(mean) - mean - sp.special.gammaln(meanvarbtran + 1.))


# In[135]:

def retr_datacntshist(varb, mean, offs):
    
    varbtran = varb - offs

    if offs <= 0.:
        return Inf
    
    datacntshist = datacntshistglob * exp(varbtran * log(mean) - mean - sp.special.gammaln(varbtran + 1.))
    
    return datacntshist


# In[136]:

def retr_indxprop(samp):
    
    global indxpoplmodi, indxprop
    indxpoplmodi = choice(indxpopl)
    
    numbpnts = int(thissampvarb[indxsampnumbpnts[indxpoplmodi]])
        
    if numbpnts == maxmnumbpnts[indxpoplmodi]:
        indxprop = choice(prop, p=probpropmaxm)
    elif numbpnts == minmnumbpnts:
        indxprop = choice(prop, p=probpropminm)
    else:
        indxprop = choice(prop, p=probprop)
        


# In[ ]:




# In[137]:

def retr_pixl(bgal, lgal):

    if pixltype == 'heal':
        pixl = pixlcnvt[ang2pix(nsideheal, deg2rad(90. - bgal), deg2rad(lgal))]
    else:
        
        jlgcr = floor(nsidecart * (lgal - minmlgal) / 2. / maxmgang).astype(int)
        jbgcr = floor(nsidecart * (bgal - minmbgal) / 2. / maxmgang).astype(int)

        if isscalar(jlgcr):
            if jlgcr < 0:
                jlgcr = 0
            if jlgcr >= nsidecart:
                jlgcr = nsidecart - 1
        else:
            jlgcr[where(jlgcr < 0)] = 0
            jlgcr[where(jlgcr >= nsidecart)] = nsidecart - 1
            

        if isscalar(jbgcr):
            if jbgcr < 0:
                jbgcr = 0
            if jbgcr >= nsidecart:
                jbgcr = nsidecart - 1
        else:
            jbgcr[where(jbgcr < 0)] = 0
            jbgcr[where(jbgcr >= nsidecart)] = nsidecart - 1
            
        pixl = jbgcr * nsidecart + jlgcr


    return pixl


# In[138]:

def retr_llik(init=False):

    global thisllik, nextmodlflux, nextmodlcnts, deltllik, nextllik, thismodlcnts, modiindx
    
    if init:

        thisllik = datacnts * log(thismodlcnts) - thismodlcnts
        
    elif indxprop >= indxproppsfipara:

        # determine pixels over which to evaluate the log-likelihood
        if indxprop == indxpropnormback:
            mpixl = ipixl
            
        if indxprop == indxproppsfipara or indxprop >= indxpropbrth:
            
            if indxprop == indxproppsfipara:
                numbpnts = int(sum(thissampvarb[indxsampnumbpnts]))
                lgal = thissampvarb[concatenate(thisindxsamplgal)]
                bgal = thissampvarb[concatenate(thisindxsampbgal)]
                spec = thissampvarb[concatenate(thisindxsampspec)[indxenermodi, :]]
            else:
                numbpnts = modilgal.shape[0]
                lgal = modilgal
                bgal = modibgal
                spec = modispec
                
            xpixlclos = []
            for k in range(numbpnts):
                jspecclos = argmin(spec[0, k] - meanspecprox)
                jpixl = retr_pixl(bgal[k], lgal[k])
                xpixlclos.append(ypixl[jspecclos][jpixl])
                
            mpixl = unique(concatenate(xpixlclos))


            #print 'xpixlclos[0].size: '
            #print xpixlclos[0].size
            #print 'mpixl.size'
            #print mpixl.size
            #print
            
        # construct the mesh grid for likelihood evaluation
        if indxprop >= indxproppsfipara:
            modiindx = meshgrid(indxenermodi, mpixl, indxevtt, indexing='ij')

        # update the point source flux map
        if indxprop == indxproppsfipara or indxprop >= indxpropbrth:

            if indxprop == indxproppsfipara:
                nextpntsflux[modiindx] = 0.
            else:
                nextpntsflux[modiindx] = thispntsflux[modiindx]
                
            for k in range(numbpnts):
                
                # calculate the distance to the pixels to be updated
                dist = retr_dist(lgal[k], bgal[k], lgalgrid[xpixlclos[k]], bgalgrid[xpixlclos[k]])

                # evaluate the PSF over the set of data cubes to be updated
                if indxprop == indxproppsfipara:
                    temppsfipara = nextpsfipara
                else:
                    temppsfipara = thissampvarb[indxsamppsfipara]
                psfn = retr_psfn(temppsfipara, indxenermodi, dist, psfntype=modlpsfntype)
                                
                # update the data cubes
                for i in range(indxenermodi.size):
                    nextpntsflux[indxenermodi[i], xpixlclos[k], :] += spec[i, k] * psfn[i, :, :]
            
        if indxprop == indxpropnormback:
            
            normbacktemp = empty((numbback, 1))
            for c in indxback:
                if c == indxbackmodi:
                    normbacktemp[c, 0] = nextsampvarb[indxsampnormback[c, indxenermodi]]
                else:
                    normbacktemp[c, 0] = thissampvarb[indxsampnormback[c, indxenermodi]]
                
            nextmodlflux[modiindx] = retr_rofi_flux(normbacktemp, thispntsflux, modiindx)

        if indxprop == indxproppsfipara or indxprop >= indxpropbrth:
            nextmodlflux[modiindx] = retr_rofi_flux(thissampvarb[indxsampnormback[meshgrid(indxback, indxenermodi, indexing='ij')]],                                                     nextpntsflux, modiindx)

        nextmodlcnts[modiindx] = nextmodlflux[modiindx] * expo[modiindx] * apix * diffener[indxenermodi, None, None] # [1]
        nextllik[modiindx] = datacnts[modiindx] * log(nextmodlcnts[modiindx]) - nextmodlcnts[modiindx]
            
        if not isfinite(nextllik[modiindx]).any():
            warnings.warn('Log-likelihood went NAN!')
            
        deltllik = sum(nextllik[modiindx] - thisllik[modiindx])
        
    else:
        
        deltllik = 0.
        
    


# In[139]:

def retr_fdfn(fdfnnorm, fdfnslop, i):
               
    fluxhistmodl = fdfnnorm / diffspec[i, indxspecpivt] * diffspec[i, :] * (meanspec[i, :] / fluxpivt[i])**(-fdfnslop)
          
    return fluxhistmodl


# In[140]:

def retr_lpri(init=False):
        
    global nextlpri, thislpri, deltlpri

    if init:
        thislpri = zeros((numbpopl, numbener))
        
        for i in indxenerfdfn:
            for l in indxpopl:
                fluxhistmodl = retr_fdfn(thissampvarb[indxsampfdfnnorm[l]], thissampvarb[indxsampfdfnslop[l, i]], i)
                fluxhist = histogram(thissampvarb[thisindxsampspec[l][i, :]], binsspec[i, :])[0]
                lprbpois = fluxhist * log(fluxhistmodl) - fluxhistmodl - sp.special.gammaln(fluxhist + 1)
                thislpri[l, i] = sum(lprbpois)            
      
        nextlpri = copy(thislpri)
                
    else:
        nextlpri = copy(thislpri)
        if indxprop == indxpropfdfnnorm or indxprop == indxpropfdfnslop             or indxprop >= indxpropbrth and indxprop <= indxpropmerg:
              
            if colrprio:
                indxenertemp = indxenerfdfn
            else:
                indxenertemp = indxenermodi
            for i in indxenertemp:
                if indxprop == indxpropfdfnnorm:
                    fdfnnorm = nextsampvarb[indxsampfdfnnorm[indxpoplmodi]]
                    fdfnslop = thissampvarb[indxsampfdfnslop[indxpoplmodi, i]]
                elif indxprop == indxpropfdfnslop:
                    fdfnnorm = thissampvarb[indxsampfdfnnorm[indxpoplmodi]]
                    fdfnslop = nextsampvarb[indxsampfdfnslop[indxpoplmodi, i]]
                else:
                    fdfnnorm = thissampvarb[indxsampfdfnnorm[indxpoplmodi]]
                    fdfnslop = thissampvarb[indxsampfdfnslop[indxpoplmodi, i]]
                fluxhistmodl = retr_fdfn(fdfnnorm, fdfnslop, i)
                              
                fluxhist = histogram(thissampvarb[thisindxsampspec[indxpoplmodi][i, :]], binsspec[i, :])[0] 
                if indxprop == indxpropbrth:
                    fluxhist += histogram(modispec[i, 0], binsspec[i, :])[0]
                elif indxprop == indxpropdeth:
                    fluxhist -= histogram(-modispec[i, 0], binsspec[i, :])[0]
                elif indxprop == indxpropsplt:
                    fluxhist -= histogram(-modispec[i, 0], binsspec[i, :])[0]
                    fluxhist += histogram(modispec[i, 1:3], binsspec[i, :])[0]
                elif indxprop == indxpropmerg:
                    fluxhist -= histogram(-modispec[i, 0:2], binsspec[i, :])[0]
                    fluxhist += histogram(modispec[i, 2], binsspec[i, :])[0]
                
                if False:
                    
                    prevfluxhistmodl = retr_fdfn(thissampvarb[indxsampfdfnnorm[indxpoplmodi]], thissampvarb[indxsampfdfnslop[indxpoplmodi, i]], i)
                    get_ipython().magic(u'matplotlib inline')
                    plt.loglog(meanspec[i, :], fluxhistmodl)
                    plt.loglog(meanspec[i, :], fluxhist)
                    plt.loglog(meanspec[i, :], prevfluxhistmodl, ls='--')
                    plt.show()


                
                lprbpois = fluxhist * log(fluxhistmodl) - fluxhistmodl - sp.special.gammaln(fluxhist + 1)
                nextlpri[indxpoplmodi, i] = sum(lprbpois)


                
            
            deltlpri = sum(nextlpri[indxpoplmodi, indxenermodi] - thislpri[indxpoplmodi, indxenermodi])

                      
        else:
            deltlpri = 0.



# In[ ]:




# In[141]:

def pars_samp(indxpntsfull, samp):
    
    cnts = []
    indxsamplgal, indxsampbgal, indxsampspec, indxsampsind, indxsampcomp = retr_indx(indxpntsfull)    
    sampvarb = zeros_like(samp)
    sampvarb[indxsampnumbpnts] = samp[indxsampnumbpnts]
    sampvarb[indxsampfdfnnorm] = icdf_logt(samp[indxsampfdfnnorm], minmfdfnnorm, factfdfnnorm)
    sampvarb[indxsampfdfnslop] = icdf_atan(samp[indxsampfdfnslop], minmfdfnslop, factfdfnslop)
         
    for c in indxback:
        sampvarb[indxsampnormback[c, :]] = icdf_logt(samp[indxsampnormback[c, :]], minmnormback[c], factnormback[c])
    for k in ipsfipara:
        sampvarb[indxsamppsfipara[k]] = icdf_psfipara(samp[indxsamppsfipara[k]], k)

    listspectemp = []
    for l in indxpopl:
        sampvarb[indxsamplgal[l]] = icdf_self(samp[indxsamplgal[l]], -maxmgangmarg, 2. * maxmgangmarg)
        sampvarb[indxsampbgal[l]] = icdf_self(samp[indxsampbgal[l]], -maxmgangmarg, 2. * maxmgangmarg) 
        for i in indxenerfdfn:
            sampvarb[indxsampspec[l][i, :]] = icdf_spec(samp[indxsampspec[l][i, :]], sampvarb[indxsampfdfnslop[l, i]], minmspec[i], maxmspec[i])
            
        if colrprio:
            sampvarb[indxsampsind[l]] = icdf_atan(samp[indxsampsind[l]], minmsind, factsind)
            sampvarb[indxsampspec[l]] = retr_spec(sampvarb[indxsampspec[l][indxenerfdfn, :]], sampvarb[indxsampsind[l]])
            
        listspectemp.append(sampvarb[indxsampspec[l]])
        
        ppixl = retr_pixl(sampvarb[indxsampbgal[l]], sampvarb[indxsamplgal[l]])
    
        cntstemp = sampvarb[indxsampspec[l]][:, :, None] * expo[:, ppixl, :] * diffener[:, None, None]
        cnts.append(cntstemp)

    pntsflux = retr_pntsflux(sampvarb[concatenate(indxsamplgal)],                                            sampvarb[concatenate(indxsampbgal)],                                            concatenate(listspectemp, axis=1), sampvarb[indxsamppsfipara])
    


    totlflux = retr_rofi_flux(sampvarb[indxsampnormback], pntsflux, fullindx)
    totlcnts = totlflux * expo * apix * diffener[:, None, None] # [1]
    
    return sampvarb, ppixl, cnts, pntsflux, totlflux, totlcnts
    


# In[142]:

def retr_scalfromangl(thisangl, i, m):
    scalangl = 2. * arcsin(.5 * sqrt(2. - 2 * cos(thisangl))) / fermscalfact[i, m]
    return scalangl

def retr_anglfromscal(scalangl, i, m):
    thisangl = arccos(1. - 0.5 * (2. * sin(scalangl * fermscalfact[i, m] / 2.))**2)
    return thisangl


# In[ ]:




# In[143]:

def retr_fermpsfn():
   
    name = os.environ["PNTS_TRAN_DATA_PATH"] + '/irf/psf_P8R2_SOURCE_V6_PSF.fits'
    irfn = pf.getdata(name, 1)
    minmener = irfn['energ_lo'].squeeze() * 1e-3 # [GeV]
    maxmener = irfn['energ_hi'].squeeze() * 1e-3 # [GeV]
    enerirfn = sqrt(minmener * maxmener)

    parastrg = ['ntail', 'score', 'gcore', 'stail', 'gtail']

    global nfermformpara
    nfermformpara = 5
    nfermscalpara = 3
    
    global fermpsfipara
    fermscal = zeros((numbevtt, nfermscalpara))
    fermform = zeros((numbener, numbevtt, nfermformpara))
    fermpsfipara = zeros((numbener * nfermformpara * numbevtt))
    for m in indxevtt:
        fermscal[m, :] = pf.getdata(name, 2 + 3 * jevtt[m])['PSFSCALE']
        irfn = pf.getdata(name, 1 + 3 * jevtt[m])
        for k in range(5):
            fermform[:, m, k] = interp1d(enerirfn, mean(irfn[parastrg[k]].squeeze(), axis=0))(meanener)

            
    global fermscalfact
    fermscalfact = sqrt((fermscal[None, :, 0] * (10. * meanener[:, None])**fermscal[None, :, 2])**2 +                         fermscal[None, :, 1]**2)
    
    # convert N_tail to f_core
    for m in indxevtt:
        for i in indxener:
            fermform[i, m, 1] = retr_anglfromscal(fermform[i, m, 1], i, m) # [rad]
            fermform[i, m, 3] = retr_anglfromscal(fermform[i, m, 3], i, m) # [rad]
            fermform[i, m, 0] = 1. / (1. + fermform[i, m, 0] * fermform[i, m, 3]**2 / fermform[i, m, 1]**2)
    
    # store the fermi PSF parameters
    for m in indxevtt:
        for k in range(nfermformpara):
            fermpsfipara[m*nfermformpara*numbener+indxener*nfermformpara+k] = fermform[:, m, k]
        
    frac = fermform[:, :, 0]
    sigc = fermform[:, :, 1]
    gamc = fermform[:, :, 2]
    sigt = fermform[:, :, 3]
    gamt = fermform[:, :, 4]
    
    psfn = retr_doubking(angldisp[None, :, None], frac[:, None, :], sigc[:, None, :], gamc[:, None, :],                          sigt[:, None, :], gamt[:, None, :])
            
    return psfn


# In[ ]:




# In[144]:

def updt_samp():
    
    global thissampvarb, thispntsflux, thismodlcnts, thisindxpntsfull,         thisindxpntsempt, thisllik, thislpri

    if indxprop == indxpropfdfnnorm:
        thissampvarb[indxsampfdfnnorm[indxpoplmodi]] = nextsampvarb[indxsampfdfnnorm[indxpoplmodi]]
        thislpri[indxpoplmodi, indxenermodi] = nextlpri[indxpoplmodi, indxenermodi]

    if indxprop == indxpropfdfnslop:
 
        # update the unit sample vector
        drmcsamp[thisindxsampspec[indxpoplmodi][indxenermodi, :], -1] =             cdfn_spec(thissampvarb[thisindxsampspec[indxpoplmodi][indxenermodi, :]],                       nextsampvarb[indxsampfdfnslop[indxpoplmodi, indxenermodi]],                       minmspec[indxenermodi], maxmspec[indxenermodi])
        
        # update the sample vector
        thissampvarb[indxsampfdfnslop[indxpoplmodi, indxenermodi]] =             nextsampvarb[indxsampfdfnslop[indxpoplmodi, indxenermodi]]
            
        # update the prior register
        thislpri[indxpoplmodi, indxenermodi] = nextlpri[indxpoplmodi, indxenermodi]

    # likelihood updates
    if indxprop >= indxproppsfipara:
        thisllik[modiindx] = nextllik[modiindx]
        thismodlcnts[modiindx] = nextmodlcnts[modiindx]
        
    if indxprop == indxproppsfipara:
        thissampvarb[indxsamppsfipara[indxpsfiparamodi]] = nextpsfipara[indxpsfiparamodi]
        
    if indxprop == indxpropnormback:
        thissampvarb[indxsampnormback[indxbackmodi, indxenermodi]] =             nextsampvarb[indxsampnormback[indxbackmodi, indxenermodi]]
        
    if indxprop >= indxpropbrth or indxprop == indxproppsfipara:
        thispntsflux[modiindx] = nextpntsflux[modiindx]
        
    # transdimensinal updates
    if indxprop >= indxpropbrth and indxprop <= indxpropmerg:
        thissampvarb[indxsampnumbpnts[indxpoplmodi]] = nextsampvarb[indxsampnumbpnts[indxpoplmodi]]
        thislpri[indxpoplmodi, indxenermodi] = nextlpri[indxpoplmodi, indxenermodi]
        
    # birth
    if indxprop == indxpropbrth:
        
        # update the PS index lists
        thisindxpntsfull[indxpoplmodi].append(thisindxpntsempt[indxpoplmodi][0])
        del thisindxpntsempt[indxpoplmodi][0]

        # update the components
        thissampvarb[indxsampmodi[0]] = modilgal
        thissampvarb[indxsampmodi[1]] = modibgal
        if colrprio:
            thissampvarb[indxsampmodi[2+indxener]] = modispec
            thissampvarb[indxsampmodi[2+numbener]] = modisind
        else:
            thissampvarb[indxsampmodi[2:]] = modispec
            
        
    # death
    if indxprop == indxpropdeth:
        
        # update the PS index lists
        thisindxpntsempt[indxpoplmodi].append(killindxpnts)
        thisindxpntsfull[indxpoplmodi].remove(killindxpnts)


    # split
    if indxprop == indxpropsplt:

        # update the PS index lists
        thisindxpntsfull[indxpoplmodi].append(thisindxpntsempt[indxpoplmodi][0])
        del thisindxpntsempt[indxpoplmodi][0]
        
        # update the components
        # first component
        thissampvarb[indxinit0] = modilgal[1]
        thissampvarb[indxinit0+1] = modibgal[1]
        thissampvarb[indxinit0+2:indxinit0+2+numbener] = modispec[:, 1]
  
        # second component
        thissampvarb[indxinit1] = modilgal[2]
        thissampvarb[indxinit1+1] = modibgal[2]
        thissampvarb[indxinit1+2:indxinit1+2+numbener] = modispec[:, 2]
        
    # merge
    if indxprop == indxpropmerg:
        
        # update the PS index lists
        thisindxpntsfull[indxpoplmodi].remove(mergindxpnts1)
        thisindxpntsempt[indxpoplmodi].append(mergindxpnts1)

        # update the component
        thissampvarb[indxsampmodi[0]] = modilgal[2]
        thissampvarb[indxsampmodi[1]] = modibgal[2]
        thissampvarb[indxsampmodi[2:]] = modispec[:, 2]
        
        
    # component change
    if indxprop >= indxproplgal:  
        if indxprop == indxproplgal:
            thissampvarb[indxsampmodi] = modilgal[1]
        elif indxprop == indxpropbgal:
            thissampvarb[indxsampmodi] = modibgal[1]
        else:
            if colrprio:
                if False:
                    print 'hey'
                    print 'modispec'
                    print modispec
                    print 'modisind'
                    print modisind
                thissampvarb[indxsampmodispec] = modispec[:, 1]
                if indxprop == indxpropsind:
                    thissampvarb[indxsampmodi] = modisind
            else:
                thissampvarb[indxsampmodi] = modispec[0, 1]

    
    # update the unit sample vector
    if indxsampmodi.size > 0:
        drmcsamp[indxsampmodi, 0] = drmcsamp[indxsampmodi, 1]


        


# In[145]:

def retr_mrkrsize(spec, indxenertemp):

    mrkrsize = (spec - minmspec[indxenertemp]) / (maxmspec[indxenertemp] - minmspec[indxenertemp]) *                     (maxmmrkrsize - minmmrkrsize) + minmmrkrsize
        
    return mrkrsize


# In[146]:

def retr_postvarb(listvarb):

    shap = zeros(len(listvarb.shape), dtype=int)
    shap[0] = 3
    shap[1:] = listvarb.shape[1:]
    shap = list(shap)
    postvarb = zeros(shap)
    
    postvarb[0, :] = percentile(listvarb, 50., axis=0)
    postvarb[1, :] = percentile(listvarb, 16., axis=0)
    postvarb[2, :] = percentile(listvarb, 84., axis=0)

    return postvarb


def retr_errrvarb(postvarb):

    errr = abs(postvarb[0, :] - postvarb[1:3, :])

    return errr



# In[ ]:




# In[147]:

def retr_pairlist(lgal, bgal):
    
    pairlist = []
    for k in range(lgal.size):
        indxpnts = k + 1 + where((lgal[k+1:] < lgal[k] + spmrlbhl) &                               (lgal[k+1:] > lgal[k] - spmrlbhl) &                               (bgal[k+1:] < bgal[k] + spmrlbhl) &                               (bgal[k+1:] > bgal[k] - spmrlbhl))[0]
        for l in range(indxpnts.size):
            pairlist.append([k, indxpnts[l]])
    return pairlist


# In[148]:

def retr_prop():

    # temp
    global thislgal, thisbgal, thisspec, nextlgal0, nextlgal1, nextbgal0, nextbgal1, nextspec0, nextspec1
    global thislgal0, thisbgal0, thisspec0, thislgal1, thisbgal1, thisspec1, nextlgal, nextbgal, nextspec
    global laccfrac, thisjcbnfact, thiscombfact
        
    global nextsampvarb, nextpsfipara, mpixl, indxpsfiparamodi,         modilgal, modibgal, modispec, modiflux, modisind,         indxinit0, indxinit1, nextflux0, nextflux1,         indxenermodi, indxbackmodi,         nextflux, nextsind, nextpntsflux, modiindxindxpnts, nextindxsampslot,         indxsampmodispec, indxsampmodi, indxcompmodi,         reje, mergindxpnts1
    
    global thisindxsamplgal, thisindxsampbgal, thisindxsampspec, thisindxsampcomp 
    thisindxsamplgal, thisindxsampbgal, thisindxsampspec, thisindxsampsind, thisindxsampcomp = retr_indx(thisindxpntsfull)
    
    if verbtype > 2:
        print 'retr_prop(): '

        print 'drmcsamp'
        print drmcsamp
        
        print 'thissampvarb: '
        for k in range(thissampvarb.size):
            if k == indxcompinit:
                print
            if k > indxcompinit and (k - indxcompinit) % numbcomp == 0:
                print
            print thissampvarb[k]
        print
            
        print 'thisindxpntsfull: ', thisindxpntsfull
        print 'thisindxpntsempt: ', thisindxpntsempt  
        print 'thisindxsamplgal: ', thisindxsamplgal
        print 'thisindxsampbgal: ', thisindxsampbgal
        print 'thisindxsampspec: '
        print thisindxsampspec
        if colrprio:
            print 'thisindxsampsind: ', thisindxsampsind
        print 'thisindxsampcomp: ', thisindxsampcomp
        print
        
    # hyper-parameter changes
    # mean number of point sources
    if indxprop == indxpropfdfnnorm:
        indxsampmodi = indxsampfdfnnorm[indxpoplmodi]
        retr_gaus(indxsampmodi, stdvfdfnnorm)
        nextsampvarb[indxsampfdfnnorm] = icdf_logt(drmcsamp[indxsampmodi, -1], minmfdfnnorm, factfdfnnorm)
        if colrprio:
            indxenermodi = indxenerfdfn
        else:
            indxenermodi = indxener
        
    # flux distribution function slope
    if indxprop == indxpropfdfnslop:
        if colrprio:
            indxenermodi = indxenerfdfn
        else:
            indxenermodi = choice(indxener)
        indxsampmodi = indxsampfdfnslop[indxpoplmodi, indxenermodi]
        retr_gaus(indxsampmodi, stdvfdfnslop)
        nextsampvarb[indxsampfdfnslop[indxpoplmodi, indxenermodi]] = icdf_atan(drmcsamp[indxsampmodi, -1], minmfdfnslop, factfdfnslop)
        if colrprio:
            indxsampmodi = concatenate((indxsampmodi, thisindxsampspec[indxpoplmodi][indxener, :].flatten()))
        else:
            indxsampmodi = concatenate((array([indxsampmodi]), thisindxsampspec[indxpoplmodi][indxenermodi, :]))
            
            
        if verbtype > 2:
            print 'indxpoplmodi'
            print indxpoplmodi
            print 'indxenermodi'
            print indxenermodi
            print 'nextsampvarb[indxsampfdfnslop]'
            print nextsampvarb[indxsampfdfnslop]
            print 'indxsampmodi'
            print indxsampmodi
        
        
            
    # PSF parameter change 
    if indxprop == indxproppsfipara:
        
        # index of the PSF parameter to change
        indxpsfiparamodi = choice(ipsfipara)

        # the energy bin of the PS flux map to be modified
        indxenermodi = array([(indxpsfiparamodi % numbpsfiparaevtt) // nformpara])
        indxsampmodi = indxsamppsfipara[indxpsfiparamodi]
        retr_gaus(indxsampmodi, stdvpsfipara)
        nextpsfipara = copy(thissampvarb[indxsamppsfipara])
        nextpsfipara[indxpsfiparamodi] = icdf_psfipara(drmcsamp[indxsampmodi, -1], indxpsfiparamodi)

        modilgal = thissampvarb[thisindxsamplgal[indxpoplmodi]]
        modibgal = thissampvarb[thisindxsampbgal[indxpoplmodi]]
        modispec = thissampvarb[thisindxsampspec[indxpoplmodi]]
        
        if verbtype > 1:
            
            print 'thissampvarb[indxsamppsfipara]: ', thissampvarb[indxsamppsfipara]
            print 'nextpsfipara: ', nextpsfipara
            print 'indxpsfiparamodi: ', indxpsfiparamodi
            print 'thissampvarb[indxsampmodi]: ', thissampvarb[indxsampmodi]
            print 'nextpsfipara: ', nextpsfipara[indxpsfiparamodi]
            print 

        
    # background changes
    
    # diffuse model
    if indxprop == indxpropnormback:

        # determine the sample index to be changed
        indxenermodi = choice(indxener)
        indxbackmodi = choice(indxback)
        indxsampmodi = indxsampnormback[indxbackmodi, indxenermodi]
        
        # propose
        retr_gaus(indxsampmodi, stdvback)

        # transform back from the unit space
        nextsampvarb[indxsampmodi] = icdf_logt(drmcsamp[indxsampmodi, -1],                                                minmnormback[indxbackmodi], factnormback[indxbackmodi])

        if verbtype > 1:
            print 'indxsampmodi: ', indxsampmodi
            print 'nextsampvarb[indxsampmodi]: ', nextsampvarb[indxsampmodi]

       
    
        
    # birth
    if indxprop == indxpropbrth:

        # change the number of PS
        nextsampvarb[indxsampnumbpnts[indxpoplmodi]] = thissampvarb[indxsampnumbpnts[indxpoplmodi]] + 1
    
        # initial sample index to add the new PS
        indxbrth = indxcompinit + maxmnumbcomp * indxpoplmodi + thisindxpntsempt[indxpoplmodi][0] * numbcomp
        
        # sample auxiliary variables
        if colrprio:
            numbauxipara = numbcompcolr
        else:
            numbauxipara = numbcomp
        auxipara = rand(numbauxipara)

        if colrprio:
            drmcsamp[indxbrth:indxbrth+2, -1] = auxipara[0:2]
            drmcsamp[indxbrth+2+indxenerfdfn, -1] = auxipara[-2]
            drmcsamp[indxbrth+numbcomp-1, -1] = auxipara[-1]
        else:
            drmcsamp[indxbrth:indxbrth+numbcomp, -1] = auxipara

        # sample indices to be modified
        indxsampmodi = arange(indxbrth, indxbrth + numbcomp, dtype=int)

        # modification catalog
        modilgal = empty(1)
        modibgal = empty(1)
        if colrprio:
            modiflux = empty(1)
            modisind = empty(1)
        modispec = zeros((numbener, 1))
        
        modilgal[0] = icdf_self(drmcsamp[indxbrth, -1], -maxmgangmarg, 2. * maxmgangmarg)
        modibgal[0] = icdf_self(drmcsamp[indxbrth+1, -1], -maxmgangmarg, 2. * maxmgangmarg)

        if colrprio:
            modiflux[0] = icdf_spec(drmcsamp[indxbrth+2+indxenerfdfn, -1],                                     thissampvarb[indxsampfdfnslop[indxpoplmodi, indxenerfdfn]],                                     minmspec[indxenerfdfn], maxmspec[indxenerfdfn])
            modisind[0] = icdf_atan(drmcsamp[indxbrth+numbcomp-1, -1], minmsind, factsind)
            modispec[:, 0] = retr_spec(modiflux[0], modisind[0]).flatten()
        else:
            for i in indxener:
                modispec[i, 0] = icdf_spec(drmcsamp[indxbrth+2+i, -1],                                            thissampvarb[indxsampfdfnslop[indxpoplmodi, i]],                                            minmspec[i], maxmspec[i])
    
        if verbtype > 1:
            print 'auxipara: ', auxipara
            print 'modilgal: ', modilgal
            print 'modibgal: ', modibgal
            print 'modispec: '
            print modispec
            print
            
    # kill
    if indxprop == indxpropdeth:
        
        # change the number of PS
        nextsampvarb[indxsampnumbpnts[indxpoplmodi]] = thissampvarb[indxsampnumbpnts[indxpoplmodi]] - 1

        # occupied PS index to be killed
        killindxindxpnts = choice(arange(thissampvarb[indxsampnumbpnts[indxpoplmodi]], dtype=int))
        
        # PS index to be killed
        global killindxpnts
        killindxpnts = thisindxpntsfull[indxpoplmodi][killindxindxpnts]
        
        # sample indices to be modified 
        indxsampmodi = array([])
            
        # modification catalog
        modilgal = empty(1)
        modibgal = empty(1)
        modispec = zeros((numbener, 1))
        modilgal[0] = thissampvarb[thisindxsamplgal[indxpoplmodi][killindxindxpnts]]
        modibgal[0] = thissampvarb[thisindxsampbgal[indxpoplmodi][killindxindxpnts]]
        modispec[:, 0] = -thissampvarb[thisindxsampspec[indxpoplmodi][:, killindxindxpnts]]

        if verbtype > 1:
            print 'killindxpnts: ', killindxpnts
            print 'killindxindxpnts: ', killindxindxpnts
            print 'modilgal: ', modilgal
            print 'modibgal: ', modibgal
            print 'modispec: '
            print modispec
            print
            
  
    # split
    if indxprop == indxpropsplt:
        
        nextsampvarb[indxsampnumbpnts[indxpoplmodi]] = thissampvarb[indxsampnumbpnts[indxpoplmodi]] + 1
        
        # determine which point source to split
        #global spltindxindxpnts        
        spltindxindxpnts = choice(arange(thissampvarb[indxsampnumbpnts[indxpoplmodi]], dtype=int))
        spltindxpnts = thisindxpntsfull[indxpoplmodi][spltindxindxpnts]
    
        # update the sample vector
        indxinit0 = indxcompinit + maxmnumbcomp * indxpoplmodi + thisindxpntsfull[indxpoplmodi][spltindxindxpnts] * numbcomp
        indxfinl0 = indxinit0 + numbcomp
        indxinit1 = indxcompinit + maxmnumbcomp * indxpoplmodi + thisindxpntsempt[indxpoplmodi][0] * numbcomp
        indxfinl1 = indxinit1 + numbcomp
        
        # determine the modified sample vector indices
        indxsampmodi = concatenate((arange(indxinit0, indxfinl0, dtype=int), arange(indxinit1, indxfinl1, dtype=int)))
        
        thislgal = thissampvarb[thisindxsamplgal[indxpoplmodi][spltindxindxpnts]]
        thisbgal = thissampvarb[thisindxsampbgal[indxpoplmodi][spltindxindxpnts]]
        thisspec = thissampvarb[thisindxsampspec[indxpoplmodi][:, spltindxindxpnts]]
        
        if verbtype > 1:
            print 'spltindxindxpnts: ', spltindxindxpnts
            print 'spltindxpnts: ', spltindxpnts
            print 'indxinit0: ', indxinit0
            print 'indxfinl0: ', indxfinl0
            print 'indxinit1: ', indxinit1
            print 'indxfinl1: ', indxfinl1
            if pixltype == 'heal':
                print 'thislgal: ', thislgal
                print 'thisbgal: ', thisbgal
            else:
                print 'thislgal: ', 3600. * thislgal
                print 'thisbgal: ', 3600. * thisbgal
            print 'thisspec: ', thisspec
            
            
        # determine the new components
        auxipara = empty(numbcomp)
        auxipara[0:2] = rand(2) * spmrlbhl
        auxipara[2:] = (exp(rand(numbener)) - 1.) / (exp(1.) - 1.) * (maxmspec - minmspec) + minmspec
        
        if verbtype > 1:
            if pixltype == 'heal':
                print 'auxipara[0]: ', auxipara[0]
                print 'auxipara[1]: ', auxipara[1]
            else:
                print 'auxipara[0]: ', 3600. * auxipara[0]
                print 'auxipara[1]: ', 3600. * auxipara[1]
            print 'auxipara[2:]: ', auxipara[2:]
            print
            
        nextlgal0 = thislgal + auxipara[0]
        nextlgal1 = thislgal - auxipara[0]
        nextbgal0 = thisbgal + auxipara[1]
        nextbgal1 = thisbgal - auxipara[1]
        nextspec0 = (thisspec + auxipara[2:]) / 2.
        nextspec1 = (thisspec - auxipara[2:]) / 2.
        
        if verbtype > 1:
            if pixltype == 'heal':
                print 'nextlgal0: ', nextlgal0
                print 'nextlgal1: ', nextlgal1
                print 'nextbgal0: ', nextbgal0
                print 'nextbgal1: ', nextbgal1
            else:
                print 'nextlgal0: ', 3600. * nextlgal0
                print 'nextlgal1: ', 3600. * nextlgal1
                print 'nextbgal0: ', 3600. * nextbgal0
                print 'nextbgal1: ', 3600. * nextbgal1
            print 'nextspec0: ', nextspec0
            print 'nextspec1: ', nextspec1

            



        if abs(nextlgal0) > maxmgangmarg or abs(nextlgal1) > maxmgangmarg or         abs(nextbgal0) > maxmgangmarg or abs(nextbgal1) > maxmgangmarg or         where((nextspec0 > maxmspec) | (nextspec0 < minmspec))[0].size > 0 or         where((nextspec1 > maxmspec) | (nextspec1 < minmspec))[0].size > 0:
            reje = True
                
        if not reje:

            
            lgal = concatenate((array([nextlgal0, nextlgal1]), setdiff1d(thissampvarb[thisindxsamplgal[indxpoplmodi]], thislgal)))
            bgal = concatenate((array([nextbgal0, nextbgal1]), setdiff1d(thissampvarb[thisindxsampbgal[indxpoplmodi]], thisbgal)))
            pairlist = retr_pairlist(lgal, bgal)


            ## first new component
            drmcsamp[indxinit0, -1] = cdfn_self(nextlgal0, -maxmgangmarg, 2. * maxmgangmarg)
            drmcsamp[indxinit0+1, -1] = cdfn_self(nextbgal0, -maxmgangmarg, 2. * maxmgangmarg)
            for i in indxener:
                drmcsamp[indxinit0+2+i, -1] = cdfn_spec(nextspec0[i], thissampvarb[indxsampfdfnslop[indxpoplmodi, i]], minmspec[i], maxmspec[i])

            ## second new component
            drmcsamp[indxinit1, -1] = cdfn_self(nextlgal1, -maxmgangmarg, 2. * maxmgangmarg)
            drmcsamp[indxinit1+1, -1] = cdfn_self(nextbgal1, -maxmgangmarg, 2. * maxmgangmarg)
            for i in indxener:
                drmcsamp[indxinit1+2+i, -1] = cdfn_spec(nextspec1[i], thissampvarb[indxsampfdfnslop[indxpoplmodi, i]], minmspec[i], maxmspec[i])


            # construct the modification catalog
            modilgal = empty(3)
            modibgal = empty(3)
            modispec = empty((numbener, 3))

            ## component to be removed
            modilgal[0] = thislgal
            modibgal[0] = thisbgal
            modispec[:, 0] = -thisspec.flatten()

            ## first component to be added
            modilgal[1] = nextlgal0
            modibgal[1] = nextbgal0
            modispec[:, 1] = nextspec0.flatten()

            # second component to be added
            modilgal[2] = nextlgal1
            modibgal[2] = nextbgal1
            modispec[:, 2] = nextspec1.flatten()

        
    # merge
    if indxprop == indxpropmerg:
        
        nextsampvarb[indxsampnumbpnts[indxpoplmodi]] = thissampvarb[indxsampnumbpnts[indxpoplmodi]] - 1

        # determine the first PS to merge
        #dir2 = array([thissampvarb[thisindxsamplgal[indxpoplmodi]], thissampvarb[thisindxsampbgal[indxpoplmodi]]])
            
        lgal = thissampvarb[thisindxsamplgal[indxpoplmodi]]
        bgal = thissampvarb[thisindxsampbgal[indxpoplmodi]]
        pairlist = retr_pairlist(lgal, bgal)
        
        if verbtype > 1:
            print 'lgal'
            print lgal
            print 'bgal'
            print bgal
            print 'pairlist'
            print pairlist
            
            
        if len(pairlist) == 0:
            reje = True
        else:
            reje = False
            jpair = choice(arange(len(pairlist)))
            mergindxindxpnts0 = pairlist[jpair][0]
            mergindxindxpnts1 = pairlist[jpair][1]
  
        if not reje:

            # fisrt PS index to be merged
            mergindxpnts0 = thisindxpntsfull[indxpoplmodi][mergindxindxpnts0]
            mergindxsampinit0 = indxcompinit + mergindxpnts0 * numbcomp

            # second PS index to be merged
            mergindxpnts1 = thisindxpntsfull[indxpoplmodi][mergindxindxpnts1]
            mergindxsampinit1 = indxcompinit + mergindxpnts1 * numbcomp

            # determine the modified sample vector indices
            indxinit0 = indxcompinit + numbcomp * mergindxpnts0
            indxfinl0 = indxinit0 + numbcomp
            indxinit1 = indxcompinit + numbcomp * mergindxpnts1
            indxfinl1 = indxinit1 + numbcomp

            indxsampmodi = arange(indxinit0, indxfinl0)

            # indices of the PS to be merges
            mergindxpnts = sort(array([mergindxpnts0, mergindxpnts1], dtype=int))

            thislgal0 = thissampvarb[thisindxsamplgal[indxpoplmodi][mergindxindxpnts0]]
            thisbgal0 = thissampvarb[thisindxsampbgal[indxpoplmodi][mergindxindxpnts0]]
            thisspec0 = thissampvarb[thisindxsampspec[indxpoplmodi][:, mergindxindxpnts0]]

            thislgal1 = thissampvarb[thisindxsamplgal[indxpoplmodi][mergindxindxpnts1]]
            thisbgal1 = thissampvarb[thisindxsampbgal[indxpoplmodi][mergindxindxpnts1]]
            thisspec1 = thissampvarb[thisindxsampspec[indxpoplmodi][:, mergindxindxpnts1]]

            # auxiliary component
            auxipara = zeros(numbcomp)
            auxipara[0] = (thislgal0 - thislgal1) / 2.
            auxipara[1] = (thisbgal0 - thisbgal1) / 2.
            auxipara[2:] = thisspec0 - thisspec1

            # merged PS
            nextlgal = (thislgal0 + thislgal1) / 2.
            nextbgal = (thisbgal0 + thisbgal1) / 2.
            nextspec = thisspec0 + thisspec1
            
            drmcsamp[indxinit0, -1] = cdfn_self(nextlgal, -maxmgangmarg, 2. * maxmgangmarg)
            drmcsamp[indxinit0+1, -1] = cdfn_self(nextbgal, -maxmgangmarg, 2. * maxmgangmarg)
            for i in indxener:
                drmcsamp[indxinit0+2+i, -1] = cdfn_spec(nextspec[i], thissampvarb[indxsampfdfnslop[indxpoplmodi, i]], minmspec[i], maxmspec[i])

            # construct the modification catalog
            modilgal = empty(3)
            modibgal = empty(3)
            modispec = empty((numbener, 3))

            ## first component to be merged
            modilgal[0] = thislgal0
            modibgal[0] = thisbgal0
            modispec[:, 0] = -thisspec0.flatten()

            ## first component to be merged
            modilgal[1] = thislgal1
            modibgal[1] = thisbgal1
            modispec[:, 1] = -thisspec1.flatten()

            ## component to be added
            modilgal[2] = nextlgal
            modibgal[2] = nextbgal
            modispec[:, 2] = nextspec.flatten()

            if verbtype > 1:
                print 'mergindxpnts0: ', mergindxpnts0
                print 'mergindxindxpnts0: ', mergindxindxpnts0
                print 'mergindxpnts1: ', mergindxpnts1
                print 'mergindxindxpnts1: ', mergindxindxpnts1
                print 'indxinit0: ', indxinit0
                print 'indxfinl0: ', indxfinl0
                print 'indxinit1: ', indxinit1
                print 'indxfinl1: ', indxfinl1
                if pixltype == 'heal':
                    print 'thislgal0: ', thislgal0
                    print 'thisbgal0: ', thisbgal0
                    print 'thislgal1: ', thislgal1
                    print 'thisbgal1: ', thisbgal1
                else:
                    print 'thislgal0: ', 3600. * thislgal0
                    print 'thisbgal0: ', 3600. * thisbgal0
                    print 'thislgal1: ', 3600. * thislgal1
                    print 'thisbgal1: ', 3600. * thisbgal1 
                print 'thisspec0: ', thisspec0
                print 'thisspec1: ', thisspec1

                if pixltype == 'heal':
                    print 'nextlgal: ', nextlgal
                    print 'nextbgal: ', nextbgal
                    print 'auxipara[0]: ', auxipara[0]
                    print 'auxipara[1]: ', auxipara[1]
                else:
                    print 'nextlgal: ', 3600. * nextlgal
                    print 'nextbgal: ', 3600. * nextbgal
                    print 'auxipara[0]: ', 3600. * auxipara[0]
                    print 'auxipara[1]: ', 3600. * auxipara[1]
                print 'nextspec: ', nextspec
                print 'auxipara[2:]: ', auxipara[2:]
                print

    # component change
    if indxprop >= indxproplgal:     
        
        if indxprop == indxproplgal or indxprop == indxpropbgal:
            if indxprop == indxproplgal:
                indxcompmodi = 0
            else:
                indxcompmodi = 1
            indxenermodi = indxener
        else:
            if colrprio:
                indxenermodi = indxener
                if indxprop == indxpropspec:
                    indxcompmodi = 2 + indxenerfdfn
                elif indxprop == indxpropsind:
                    indxcompmodi = array([2 + numbener])
            else:
                indxenermodi = choice(indxener)
                indxcompmodi = indxenermodi + 2
            
        # occupied PS index to be modified
        modiindxindxpnts = choice(arange(thissampvarb[indxsampnumbpnts[indxpoplmodi]], dtype=int))
        
        # PS index to be modified
        modiindxpnts = thisindxpntsfull[indxpoplmodi][modiindxindxpnts]
        
        # initial sample index of the PS to be modified
        indxsampmodiinit = indxcompinit + maxmnumbcomp * indxpoplmodi + modiindxpnts * numbcomp
        
        # sample index to be modified
        indxsampmodi = indxsampmodiinit + indxcompmodi
        if colrprio:
            indxsampmodispec = indxsampmodiinit + 2 + indxener
        
        # propose
        if indxprop == indxpropspec:
            retr_gaus(indxsampmodi, stdvspec)
        else:
            retr_gaus(indxsampmodi, stdvlbhl) 

        # modification catalog
        modilgal = empty(2)
        modibgal = empty(2)
        modispec = empty((indxenermodi.size, 2))
  
        if colrprio:
            thisflux = thissampvarb[thisindxsampspec[indxpoplmodi][indxenerfdfn, modiindxindxpnts]]
            thissind = thissampvarb[thisindxsampsind[indxpoplmodi][modiindxindxpnts]]
            thisspec = retr_spec(thisflux, thissind)
        else:
            thisspec = thissampvarb[thisindxsampspec[indxpoplmodi][indxenermodi, modiindxindxpnts]]
            
        modispec[:, 0] = -thisspec.flatten()
        if indxprop == indxproplgal or indxprop == indxpropbgal:
            if indxcompmodi == 0:
                modilgal[0] = thissampvarb[thisindxsamplgal[indxpoplmodi][modiindxindxpnts]]
                modilgal[1] = icdf_self(drmcsamp[indxsampmodi, -1], -maxmgangmarg, 2. * maxmgangmarg)
                modibgal[:] = thissampvarb[thisindxsampbgal[indxpoplmodi][modiindxindxpnts]]
            else:
                modilgal[:] = thissampvarb[thisindxsamplgal[indxpoplmodi][modiindxindxpnts]]
                modibgal[0] = thissampvarb[thisindxsampbgal[indxpoplmodi][modiindxindxpnts]]
                modibgal[1] = icdf_self(drmcsamp[indxsampmodi, -1], -maxmgangmarg, 2. * maxmgangmarg)
            modispec[:, 1] = thisspec.flatten()
        else:
            modilgal[:] = thissampvarb[thisindxsamplgal[indxpoplmodi][modiindxindxpnts]]
            modibgal[:] = thissampvarb[thisindxsampbgal[indxpoplmodi][modiindxindxpnts]]
            if colrprio:
                if indxprop == indxpropspec:
                    modiflux = icdf_spec(drmcsamp[indxsampmodi, -1], thissampvarb[indxsampfdfnslop[indxpoplmodi, indxenerfdfn]], 
                                         minmspec[indxenerfdfn], maxmspec[indxenerfdfn])
                    modisind = thissampvarb[thisindxsampsind[indxpoplmodi][modiindxindxpnts]]
                else:
                    modiflux = thissampvarb[thisindxsampspec[indxpoplmodi][indxenerfdfn, modiindxindxpnts]]
                    modisind = icdf_atan(drmcsamp[indxsampmodi, -1], minmsind, factsind)

                modispec[:, 1] = retr_spec(modiflux, modisind).flatten()
            else:
                modispec[:, 1] = icdf_spec(drmcsamp[indxsampmodi, -1],                                            thissampvarb[indxsampfdfnslop[indxpoplmodi, indxenermodi]],                                            minmspec[indxenermodi], maxmspec[indxenermodi])

                
        # log
        if verbtype > 1:
            print 'modilgal: ', modilgal
            print 'modibgal: ', modibgal
            print 'modispec: '
            print modispec
            print 'indxcompmodi: ', indxcompmodi
            print 'modiindxindxpnts: ', modiindxindxpnts
            print 'modiindxpnts: ', modiindxpnts


    # energy bin in which to evaluate the log-likelihood
    if indxpropbrth <= indxprop <= indxpropmerg:
        indxenermodi = arange(numbener)

    if type(indxenermodi) == int64:
        indxenermodi = array([indxenermodi])

    if verbtype > 1:
        print 'indxsampmodi: ', indxsampmodi
        print 'indxenermodi: ', indxenermodi

    # auxiliary variable density fraction and jacobian
    global laccfrac
    if (indxprop == indxpropsplt or indxprop == indxpropmerg) and not reje:

        spltcombfact = log(thissampvarb[indxsampnumbpnts[indxpoplmodi]]**2 / len(pairlist))
        
        if indxprop == indxpropsplt:
            thiscombfact = spltcombfact 
            thisjcbnfact = spltjcbnfact
        else:
            thiscombfact = -spltcombfact 
            thisjcbnfact = -spltjcbnfact


        laccfrac = thisjcbnfact + thiscombfact

        listnumbpair[j] = len(pairlist)
        listjcbnfact[j] = thisjcbnfact
        listcombfact[j] = thiscombfact
        listauxipara[j, :] = auxipara
        listlaccfrac[j] = laccfrac

    else:
        laccfrac = 0.  
        


# In[ ]:




# In[ ]:




# In[149]:

def pair_catl(truelgal, truebgal, truespec, modllgal, modlbgal, modlspec):

    indxmodl = zeros_like(truelgal, dtype=int) - 1
    dir2 = array([modllgal, modlbgal])
    for k in range(truelgal.size):
        dir1 = array([truelgal[k], truebgal[k]])
        dist = angdist(dir1, dir2, lonlat=True)
        jdist = argmin(dist) 
        if dist[jdist] < deg2rad(0.5):
            indxmodl[k] = jdist

    jtruepntsbias = where(amax(abs(modlspec[:, indxmodl] - truespec) / truespec, axis=0) > 1.2)[0]
    jtruepntsmiss = where(indxmodl == -1)[0]
    
    return indxmodl, jtruepntsbias, jtruepntsmiss


# In[150]:

def retr_fgl3():
        
    path = os.environ["PNTS_TRAN_DATA_PATH"] + '/catl/gll_psc_v16.fit'

    fgl3 = pf.getdata(path)
    
    fgl3numbpnts = fgl3['glon'].size
    
    fgl3lgal = fgl3['glon']
    fgl3lgal = ((fgl3lgal - 180.) % 360.) - 180.

    fgl3bgal = fgl3['glat']

    fgl3axisstdv = (fgl3['Conf_68_SemiMinor'] + fgl3['Conf_68_SemiMajor']) * 0.5
    fgl3anglstdv = deg2rad(fgl3['Conf_68_PosAng']) # [rad]
    fgl3lgalstdv = fgl3axisstdv * abs(cos(fgl3anglstdv))
    fgl3bgalstdv = fgl3axisstdv * abs(sin(fgl3anglstdv))

    fgl3sind = fgl3['Spectral_Index']
    
    fgl3spectype = fgl3['SpectrumType']
    fgl3scur = fgl3['beta']
    fgl3scut = fgl3['Cutoff'] * 1e-3
    
    fgl3timevari = fgl3['Variability_Index']
    
    fgl3spectemp = stack((fgl3['Flux100_300'],                           fgl3['Flux300_1000'],                           fgl3['Flux1000_3000'],                           fgl3['Flux3000_10000'],                           fgl3['Flux10000_100000']))[jener, :] / diffener[:, None]
    fgl3specstdv = stack((fgl3['Unc_Flux100_300'],                           fgl3['Unc_Flux300_1000'],                           fgl3['Unc_Flux1000_3000'],                           fgl3['Unc_Flux3000_10000'],                           fgl3['Unc_Flux10000_100000']))[jener, :, :] / diffener[:, None, None]
    
    fgl3spec = zeros((3, numbener, fgl3numbpnts))
    fgl3spec[0, :, :] = fgl3spectemp
    fgl3spec[1, :, :] = fgl3spectemp - fgl3specstdv[:, :, 0]
    fgl3spec[2, :, :] = fgl3spectemp + fgl3specstdv[:, :, 1]
    
    # get PS counts
    ppixl = retr_pixl(fgl3bgal, fgl3lgal)
    fgl3cnts = fgl3spec[0, :, :, None] * expo[:, ppixl, :] * diffener[:, None, None]
    fgl3gang = tdpy_util.retr_gang(fgl3lgal, fgl3bgal)
    
    return fgl3lgal, fgl3bgal, fgl3spec, fgl3gang, fgl3cnts,         fgl3timevari, fgl3sind, fgl3spectype, fgl3scur, fgl3scut


# In[151]:

def retr_rtag(indxprocwork):
    
    if indxprocwork == None:
        rtag = 'A_%d_%d_%d_%d_%s_%s_%s' % (numbproc, numbswep, numbburn, factthin, datatype, regitype, modlpsfntype)
    else:
        rtag = '%d_%d_%d_%d_%d_%s_%s_%s' % (indxprocwork, numbproc, numbswep, numbburn, factthin, datatype, regitype, modlpsfntype)
        
    return rtag


# In[152]:

def main(indxprocwork):

    timereal = time.time()
    timeproc = time.clock()
    
    # re-seed the random number generator for the process
    seed()
    
    # construct the run tag
    global rtag
    rtag = retr_rtag(indxprocwork)
    
    # initialize the sample vector 
    if randinit or not trueinfo:
        if initnumbpnts != None:
            thisnumbpnts = initnumbpnts
        else:
            thisnumbpnts = empty(numbpopl, dtype=int)
            for l in indxpopl:
                thisnumbpnts[l] = choice(arange(minmnumbpnts, maxmnumbpnts[l] + 1))
    else:
        thisnumbpnts = truenumbpnts
        
    global thisindxsamplgal, thisindxsampbgal, thisindxsampspec, thisindxsampsind, thisindxsampcomp
    global thissampvarb, thisindxpntsfull, thisindxpntsempt
    
    thisindxpntsfull = []
    thisindxpntsempt = []
    for l in indxpopl:
        thisindxpntsfull.append(range(thisnumbpnts[l]))
        thisindxpntsempt.append(range(thisnumbpnts[l], maxmnumbpnts[l]))
    thisindxsamplgal, thisindxsampbgal, thisindxsampspec, thisindxsampsind, thisindxsampcomp = retr_indx(thisindxpntsfull)
      
    if verbtype > 2:
        print 'thisindxpntsfull: ', thisindxpntsfull
        print 'thisindxpntsempt: ', thisindxpntsempt  
        print 'thisindxsamplgal: ', thisindxsamplgal
        print 'thisindxsampbgal: ', thisindxsampbgal
        print 'thisindxsampspec: '
        print thisindxsampspec
        if colrprio:
            print 'thisindxsampsind: ', thisindxsampsind
        print 'thisindxsampcomp: ', thisindxsampcomp

    global drmcsamp
    drmcsamp = zeros((maxmsampsize, 2))
    
    drmcsamp[indxsampnumbpnts, 0] = thisnumbpnts
    drmcsamp[indxsampfdfnnorm, 0] = rand(numbpopl)
    if trueinfo and datatype == 'mock':
        drmcsamp[indxsampfdfnslop, 0] = cdfn_atan(mocksampvarb[indxsampfdfnslop], minmfdfnslop, factfdfnslop)
    else:
        drmcsamp[indxsampfdfnslop, 0] = rand(numbpopl * numbener).reshape((numbpopl, numbener))
    drmcsamp[indxsampnormback, 0] = rand(numbback * numbener).reshape((numbback, numbener))
    if randinit or not trueinfo or truepsfipara == None:
        drmcsamp[indxsamppsfipara, 0] = rand(numbpsfipara)
    else:
        for k in ipsfipara:
            drmcsamp[indxsamppsfipara[k], 0] = cdfn_psfipara(truepsfipara[k], k)
        
    for l in indxpopl:
        if pntscntr:
            drmcsamp[thisindxsampcomp[l], 0] = 0.5
        else:
            if randinit or not trueinfo:
                drmcsamp[thisindxsampcomp[l], 0] = rand(thisindxsampcomp[l].size)
            else:
                drmcsamp[thisindxsamplgal[l], 0] = copy(cdfn_self(truelgal[l], -maxmgangmarg, 2. * maxmgangmarg))
                drmcsamp[thisindxsampbgal[l], 0] = copy(cdfn_self(truebgal[l], -maxmgangmarg, 2. * maxmgangmarg))  
                if datatype == 'mock':
                    drmcsamp[thisindxsampspec[l], 0] = copy(mocksamp[mockindxsampspec[l]])
                    if colrprio:
                        drmcsamp[thisindxsampsind[l], 0] = copy(mocksamp[mockindxsampsind[l]])
                else:
                    for i in indxenerfdfn:
                        fdfnsloptemp = icdf_atan(drmcsamp[indxsampfdfnslop[l, i], 0], minmfdfnslop, factfdfnslop)
                        drmcsamp[thisindxsampspec[l][i, :], 0] = copy(cdfn_spec(truespec[l][0, i, :],                                                                                 fdfnsloptemp, minmspec[i], maxmspec[i]))



    global thismodlcnts, thispntsflux, nextpntsflux, nextmodlflux, nextmodlcnts, nextllik
    
    
    thissampvarb, thisppixl, thiscnts, thispntsflux,         thismodlflux, thismodlcnts = pars_samp(thisindxpntsfull, drmcsamp[:, 0])



    nextpntsflux = zeros_like(thispntsflux)
    nextmodlflux = zeros_like(thispntsflux)
    nextmodlcnts = zeros_like(thispntsflux)
    nextllik = zeros_like(thispntsflux)

    global nextsampvarb
    nextsampvarb = copy(thissampvarb)
    
    if verbtype > 1:
        print 'thissampvarb: ', thissampvarb
        
    # sampler setup
    # auxiliary variable standard deviation for merge/split
    global maxmdistpnts
    maxmdistpnts = 2. # [deg]
 
    listchan = rjmc(indxprocwork)
    
    timereal = time.time() - timereal
    timeproc = time.clock() - timeproc
    
    listchan.append(timereal)
    listchan.append(timeproc)
    
    return listchan


# In[153]:

def retr_gaus(indxsamp, stdv):
    
    if fracrand > 0.:
        if rand() < fracrand:
            drmcsamp[indxsamp, 1] = rand()
        else:
            drmcsamp[indxsamp, 1] = drmcsamp[indxsamp, 0] + normal(scale=stdv)
    else:
        drmcsamp[indxsamp, 1] = drmcsamp[indxsamp, 0] + normal(scale=stdv)


# In[154]:

def retr_dist(lgal0, bgal0, lgal1, bgal1):
    
    if pixltype == 'heal':
        dir1 = array([lgal0, bgal0])
        dir2 = array([lgal1, bgal1])
        dist = angdist(dir1, dir2, lonlat=True) # [rad]
    else:
        dist = deg2rad(sqrt((lgal0 - lgal1)**2 + (bgal0 - bgal1)**2))

    return dist
        


# In[155]:

def rjmc(indxprocwork):
        
    global reje
    
    # temp
    global accpprob, listaccp
    
    
    # sweeps to be saved
    global save
    save = zeros(numbswep, dtype=bool)
    jswep = arange(numbburn, numbswep, factthin)
    save[jswep] = True
    
    sampindx = zeros(numbswep, dtype=int)
    sampindx[jswep] = arange(numbsamp)

    listsampvarb = zeros((numbsamp, maxmsampsize)) + -1.
    listindxprop = zeros(numbswep)
    listchro = zeros((numbswep, 4))
    listllik = zeros(numbsamp)
    listlprising = zeros(numbsamp)
    listlpri = zeros(numbsamp)
    listaccp = zeros(numbswep, dtype=bool)
    listaccpspec = []
    listindxsampmodi = zeros(numbswep, dtype=int)
    listmodlcnts = zeros((numbsamp, ngpixl))
    listpntsfluxmean = zeros((numbsamp, numbener))
    listindxpntsfull = []
    
    global listauxipara, listlaccfrac, listcombfact, listjcbnfact, listnumbpair
    listauxipara = zeros((numbswep, numbcomp))
    listlaccfrac = zeros(numbswep)
    listnumbpair = zeros(numbswep)
    listjcbnfact = zeros(numbswep)
    listcombfact = zeros(numbswep)

    # initialize the chain
    retr_llik(init=True)
    retr_lpri(init=True)

    # current sample index
    thiscntr = -1
    
    histdeltllik = [[[] for k in range(10)] for l in range(10)]
    histdeltlpri = [[[] for k in range(10)] for l in range(10)]
    
    

    global j
    j = 0
    while j < numbswep:
        

        tim0 = time.time()
        
        if verbtype > 1:
            print
            print '-' * 10
            print 'Sweep %d' % j

        thismakefram = (j % plotperd == 0) and indxprocwork == int(float(j) / numbswep * numbproc) and makeplot
        reje = False
    
        # choose a proposal type
        retr_indxprop(drmcsamp[:, 0])
            
        # save the proposal type
        listindxprop[j] = indxprop
        if verbtype > 1:
            print 'indxprop: ', strgprop[indxprop]
        
        
        if verbtype > 1:        
            print
            print '-----'
            print 'Proposing...'
            print

        # propose the next sample
        timebegn = time.time()
        retr_prop()
        timefinl = time.time()
        listchro[j, 1] = timefinl - timebegn

        # plot the current sample
        if thismakefram:
            print
            print 'Process %d is in queue for making a frame.' % indxprocwork
            if numbproc > 1:
                lock.acquire()
            print 'Process %d started making a frame' % indxprocwork
            plot_samp()
            print 'Process %d finished making a frame' % indxprocwork
            if numbproc > 1:
                lock.release()
            
        # reject the sample if proposal is outside the prior
        if indxprop != indxpropbrth and indxprop != indxpropdeth and not reje:
            if where((drmcsamp[indxsampmodi, 1] < 0.) | (drmcsamp[indxsampmodi, 1] > 1.))[0].size > 0:
                reje = True
        if indxprop == indxproppsfipara:
            if modlpsfntype == 'doubking':
                if nextpsfipara[1] > nextpsfipara[3]:
                    reje = True
            elif modlpsfntype == 'doubgaus':
                if nextpsfipara[1] > nextpsfipara[2]:
                    reje = True
                
  
            
        if not reje:

            # evaluate the log-prior
            timebegn = time.time()
            retr_lpri()
            timefinl = time.time()
            listchro[j, 2] = timefinl - timebegn

            # evaluate the log-likelihood
            timebegn = time.time()
            retr_llik()          
            timefinl = time.time()
            listchro[j, 3] = timefinl - timebegn
            
            # evaluate the acceptance probability
            accpprob = exp(deltllik + deltlpri + laccfrac)

            if verbtype > 1:
                print 'deltlpri'
                print deltlpri
                print 'deltllik'
                print deltllik
                print 'laccfrac'
                print laccfrac
                print
                
        else:
            accpprob = 0.
    
    
        # accept the sample
        if accpprob >= rand():

            if verbtype > 1:
                print 'Accepted.'

            # update the current state
            updt_samp()

            listaccp[j] = True

        # reject the sample
        else:

            if verbtype > 1:
                print 'Rejected.'

            listaccp[j] = False
             
        # sanity checks
        if where((drmcsamp[1:, 0] > 1.) | (drmcsamp[1:, 0] < 0.))[0].size > 0:
            print 'Unit sample vector went outside [0,1]!'
            print 'drmcsamp'
            for k in range(maxmsampsize):
                print drmcsamp[k, :]
            return

        for l in indxpopl:
            for i in indxenerfdfn:
                if where(thissampvarb[thisindxsampspec[l][i, :]] < minmspec[i])[0].size > 0:
                    print 'Spectrum of some PS went below the prior range!'
                if where(thissampvarb[thisindxsampspec[l][i, :]] > maxmspec[i])[0].size > 0:
                    print 'Spectrum of some PS went above the prior range!'          
            
           
        if False:
            if where(nextpntsflux < 0.)[0].size > 0:
                print 'Current PS flux map went negative!'
                for i in indxener:
                    for m in indxevtt:
                        plot_heal(nextpntsflux[i, :, m], titl='thispntsflux')

            if where(nextpntsflux < 0.)[0].size > 0:
                print 'Proposed PS flux map went negative!'


        # temp
        if False:
            for i in indxener:
                for m in indxevtt:
                    plot_heal(thispntsflux[i, :, m], titl='thispntsflux')
            for i in indxener:
                for m in indxevtt:
                    plot_heal(nextpntsflux[i, :, m], titl='nextpntsflux')

            if amax(abs(errrmodlcnts)) > 0.1 and False:
                print 'Approximation error went above the limit!'



            
        # save the sample
        if save[j]:
            listsampvarb[sampindx[j], :] = thissampvarb
            listmodlcnts[sampindx[j], :] = thismodlcnts[0, gpixl, 0]
            listpntsfluxmean[sampindx[j], :] = mean(sum(thispntsflux * expo, 2) / sum(expo, 2), 1)
            listindxpntsfull.append(thisindxpntsfull)
            listllik[sampindx[j]] = sum(thisllik)
            
            lpri = 0.
            for l in indxpopl:
                numbpnts = thissampvarb[indxsampnumbpnts[l]]
                fdfnnorm = thissampvarb[indxsampfdfnnorm[l]]
                lpri += numbpnts * priofactlgalbgal + priofactfdfnslop + fdfnnormfact - log(fdfnnorm)
                for i in indxenerprio:
                    flux = thissampvarb[thisindxsampspec[l][i, :]]
                    fdfnslop = thissampvarb[indxsampfdfnslop[l, i]]
                    lpri -= log(1. + fdfnslop**2)
                    lpri += sum(log(pdfn_spec(flux, fdfnslop, minmspec[i], maxmspec[i])))
            listlpri[sampindx[j]] = lpri
            
            
            if tracsamp:
                
                numbpnts = thissampvarb[indxsampnumbpnts[0]]
                diffllikdiffpara = empty(numbpnts)
                for k in range(numbpnts):
                    diffllikdiffpara[k]
                listdiffllikdiffpara.append(diffllikdiffpara)

                tranmatr = diffllikdiffpara[:, None] * listdiffllikdiffpara[j-1][None, :]
                listtranmatr.append(tranmatr)

        # save the execution time for the sweep
        if not thismakefram:
            tim1 = time.time()
            listchro[j, 0] = tim1 - tim0

        # log the progress
        if verbtype > 0:
            thiscntr = tdpy_util.show_prog(j, numbswep, thiscntr, indxprocwork=indxprocwork)
            
            
        if diagsamp:
            plot_datacnts(0, 0, nextstat=True)
            plot_resicnts(0, 0, thisresicnts, nextstat=True)
        
        if verbtype > 1:
            print
            print
            print
            print
            print
            print
            print
            print
            print
            print
            print
            print
            
        
        
        # update the sweep counter
        j += 1

    
    if verbtype > 1:
        print 'listsampvarb: '
        print listsampvarb
    
    
    # correct the likelihoods for the constant data dependent factorial
    listllik -= sum(sp.special.gammaln(datacnts + 1))
    
    # calculate the log-evidence and relative entropy using the harmonic mean estimator
    minmlistllik = amin(listllik)
    levi = -log(mean(1. / exp(listllik - minmlistllik))) + minmlistllik
    
    info = mean(listllik) - levi

    listchan = [listsampvarb, listindxprop, listchro, listllik, listlpri, listaccp,                 listmodlcnts, listindxpntsfull, listindxsampmodi,                 listauxipara, listlaccfrac, listnumbpair, listjcbnfact, listcombfact, levi, info, listpntsfluxmean]
    
    
    return listchan


# In[156]:

def retr_propstrg():
    
    propstrg = [r'$\mu$', r'$\alpha$', r'$\beta$',                  'PSF', 'Diffuse Norm', 'Isotropic Norm', 'Birth', 'Death',                  'Split', 'Merge', 'l-update', 'b-update', 'f-update']
    
    return propstrg
    


# In[ ]:




# In[157]:

def gmrb_test(griddata):
    
    withvari = mean(var(griddata, 0))
    btwnvari = griddata.shape[0] * var(mean(griddata, 0))
    wgthvari = (1. - 1. / griddata.shape[0]) * withvari + btwnvari / griddata.shape[0]
    
    psrf = sqrt(wgthvari / withvari)

    return psrf


# In[158]:

def retr_psfn(psfipara, indxenertemp, thisangl, psfntype='doubking'):

    thisangltemp = thisangl[None, :, None]

    jpsfipara = indxenertemp[:, None] * nformpara + indxevtt[None, :] * numbpsfiparaevtt
    
    if psfntype == 'singgaus':
        sigc = psfipara[jpsfipara]
        sigc = sigc[:, None, :]
        psfn = retr_singgaus(thisangltemp, sigc)

    elif psfntype == 'singking':
        sigc = psfipara[jpsfipara]
        gamc = psfipara[jpsfipara+1]
        sigc = sigc[:, None, :]
        gamc = gamc[:, None, :]
        psfn = retr_singking(thisangltemp, sigc, gamc)
        
    elif psfntype == 'doubgaus':
        frac = psfipara[jpsfipara]
        sigc = psfipara[jpsfipara+1]
        sigt = psfipara[jpsfipara+2]
        frac = frac[:, None, :]
        sigc = sigc[:, None, :]
        sigt = sigt[:, None, :]
        psfn = retr_doubgaus(thisangltemp, frac, sigc, sigt)

    elif psfntype == 'gausking':
        frac = psfipara[jpsfipara]
        sigc = psfipara[jpsfipara+1]
        sigt = psfipara[jpsfipara+2]
        gamt = psfipara[jpsfipara+3]
        frac = frac[:, None, :]
        sigc = sigc[:, None, :]
        sigt = sigt[:, None, :]
        gamt = gamt[:, None, :]
        psfn = retr_gausking(thisangltemp, frac, sigc, sigt, gamt)
        
    elif psfntype == 'doubking':
        frac = psfipara[jpsfipara]
        sigc = psfipara[jpsfipara+1]
        gamc = psfipara[jpsfipara+2]
        sigt = psfipara[jpsfipara+3]
        gamt = psfipara[jpsfipara+4]
        frac = frac[:, None, :]
        sigc = sigc[:, None, :]
        gamc = gamc[:, None, :]
        sigt = sigt[:, None, :]
        gamt = gamt[:, None, :]
        psfn = retr_doubking(thisangltemp, frac, sigc, gamc, sigt, gamt)
            
    return psfn


# In[159]:

def retr_singgaus(scaldevi, sigc):
    
    psfn = 1. / 2. / pi / sigc**2 * exp(-0.5 * scaldevi**2 / sigc**2)

    return psfn


def retr_singking(scaldevi, sigc, gamc):
    
    psfn = 1. / 2. / pi / sigc**2 * (1. - 1. / gamc) * (1. + scaldevi**2 / 2. / gamc / sigc**2)**(-gamc)

    return psfn


def retr_doubgaus(scaldevi, frac, sigc, sigt):
    
    psfn = frac / 2. / pi / sigc**2 * exp(-0.5 * scaldevi**2 / sigc**2) +                 (1. - frac) / 2. / pi / sigc**2 * exp(-0.5 * scaldevi**2 / sigc**2)

    return psfn


def retr_gausking(scaldevi, frac, sigc, sigt, gamt):

    psfn = frac / 2. / pi / sigc**2 * exp(-0.5 * scaldevi**2 / sigc**2) +                 (1. - frac) / 2. / pi / sigt**2 * (1. - 1. / gamt) * (1. + scaldevi**2 / 2. / gamt / sigt**2)**(-gamt)
    
    return psfn


def retr_doubking(scaldevi, frac, sigc, gamc, sigt, gamt):

    psfn = frac / 2. / pi / sigc**2 * (1. - 1. / gamc) * (1. + scaldevi**2 / 2. / gamc / sigc**2)**(-gamc) +                 (1. - frac) / 2. / pi / sigt**2 * (1. - 1. / gamt) * (1. + scaldevi**2 / 2. / gamt / sigt**2)**(-gamt)
    
    return psfn



# In[160]:

def plot_evidtest():
    
    minmgain = -1.
    maxmgain = 5.
    minmdevi = 0.
    maxmdevi = 5.
    gain = linspace(minmgain, maxmgain, 100)
    devi = linspace(minmdevi, maxmdevi, 100)

    evid = log(sqrt(1. + exp(2. * gain[None, :])) *                exp(-devi[:, None]**2 / 2. / (1. + 1. / exp(2. * gain[None, :]))))
    
    figr, axis = plt.subplots(figsize=(7, 7))
    figr.suptitle('Log-Bayesian Evidence For Lower-Dimension Model', fontsize=18)
    imag = axis.imshow(evid, extent=[minmgain, maxmgain, minmdevi, maxmdevi], cmap='winter', origin='lower')
    cset1 = plt.contourf(gain, devi, evid, cmap='winter')
    axis.set_xlabel('Information gain')
    axis.set_ylabel('Goodness of fit')
    plt.colorbar(imag, ax=axis, fraction=0.03)
    #figr.subplots_adjust(top=0.8)

    plt.savefig(plotpath + 'evidtest_' + rtag + '.png')
    plt.close(figr)
    

def plot_pntsprob(pntsprobcart, ptag, full=False, cumu=False):
    
    if cumu:
        ncoln = 1
    else:
        ncoln = 2
        
    if cumu:
        nrows = 1
    elif full:
        nrows = numbspec / 2
    else:
        nrows = 2
        
    if exprtype == 'ferm':
        strgvarb = '$f$'
        strgunit = ' [1/cm$^2$/s/GeV]'
    if exprtype == 'sdss':
        strgvarb = '$C$'
        strgunit = ' [counts]'
    titl = strgvarb + strgunit

    for l in indxpopl:
        for i in indxenerfdfn:
            figr, axgr = plt.subplots(nrows, ncoln, figsize=(ncoln * 7, nrows * 7), sharex='all', sharey='all')
            if nrows == 1:
                axgr = [axgr]            
            figr.suptitle(titl, fontsize=18)
            for a, axrw in enumerate(axgr):
                if ncoln == 1:
                    axrw = [axrw]
                for b, axis in enumerate(axrw):
                    h = a * 2 + b

                    if h < 3 or full:
                        imag = axis.imshow(pntsprobcart[:, :, l, i, h], origin='lower', cmap='Reds',                                            norm=mpl.colors.LogNorm(vmin=0.01, vmax=1), extent=extt)
                    else:
                        imag = axis.imshow(sum(pntsprobcart[:, :, l, i, 3:], 2), origin='lower', cmap='Reds',                                            norm=mpl.colors.LogNorm(vmin=0.01, vmax=1), extent=extt)

                    # vmin=0.01, vmax=1
                
                    plt.colorbar(imag, fraction=0.05, ax=axis)

                    # superimpose true PS
                    if trueinfo:
                        if h < 3 or full:
                            indxpnts = where((binsspec[i, h] < truespec[l][0, i, :]) &                                           (truespec[l][0, i, :] < binsspec[i, h+1]))[0]
                        else:
                            indxpnts = where(binsspec[i, 3] < truespec[l][0, i, :])[0]

                        mar1 = axis.scatter(truelgal[l][indxpnts],                                           truebgal[l][indxpnts],                                           s=100, alpha=0.5, marker='x', lw=2, color='g')
                        
                    axis.set_xlabel(longlabl)
                    axis.set_ylabel(latilabl)
                    axis.set_xlim([frambndrmarg, -frambndrmarg])
                    axis.set_ylim([-frambndrmarg, frambndrmarg])
                    axis.axvline(frambndr, ls='--', alpha=0.3, color='black')
                    axis.axvline(-frambndr, ls='--', alpha=0.3, color='black')
                    axis.axhline(frambndr, ls='--', alpha=0.3, color='black')
                    axis.axhline(-frambndr, ls='--', alpha=0.3, color='black')
                    if not cumu:
                        if h < 3 or full:
                            axis.set_title(tdpy_util.mexp(binsspec[i, h]) + ' $<$ ' + strgvarb + ' $<$ ' + tdpy_util.mexp(binsspec[i, h+1]))
                        else:
                            axis.set_title(tdpy_util.mexp(binsspec[i, h]) + ' $<$ ' + strgvarb)
            figr.savefig(plotpath + 'pntsbind' + ptag + '%d%d' % (l, jener[i]) + '_' + rtag + '.png')
            plt.close(figr)
        
        
def plot_king():

    figr, axgr = plt.subplots(1, 2, figsize=(12, 6))
    figr.suptitle('King Function', fontsize=20)
    for k, axis in enumerate(axgr):
        if k == 0:
            sigmlist = [0.25]
            gammlist = [1.01, 2.5, 10.]
            lloc = 3
        else:
            sigmlist = [0.1, 0.25, 1.]
            gammlist = [2.]
            lloc = 1
        for sigm in sigmlist:
            for gamm in gammlist:
                axis.plot(rad2deg(angldisp), retr_king(sigm, gamm), label=r'$\sigma = %.4g, \gamma = %.3g$' % (sigm, gamm))
        axis.legend(loc=lloc)
        axis.set_yscale('log')
        axis.set_xlabel(r'$\theta$ ' + strganglunit)
        axis.set_xlabel(r'$\mathcal{K}(\theta)$')
        plt.figtext(0.7, 0.7, '$\mathcal{K}(\theta) = \frac{1}{2\pi\sigma^2}(1-\frac{1}{\gamma}(\frac{x^2}{2\sigma^2\gamma})^{-\gamma})$')
        
    figr.subplots_adjust()
    plt.savefig(plotpath + 'king.png')
    plt.close(figr)
    

def plot_psfn(thispsfn):
    
    if exprtype == 'sdss':
        angldisptemp = rad2deg(angldisp) * 3600.
    if exprtype == 'ferm':
        angldisptemp = rad2deg(angldisp)

    with sns.color_palette("Blues", numbevtt):

        figr, axgr = plt.subplots(numbevtt, numbener, figsize=(7 * numbener, 7 * numbevtt))
        figr.suptitle(r'Point Spread Function, d$P$/d$\Omega$ [1/sr]', fontsize=20)
        if numbevtt == 1:
            axgr = [axgr]
        for m, axrw in enumerate(axgr):
            if numbener == 1:
                axrw = [axrw]
            for i, axis in enumerate(axrw):
                axis.plot(angldisptemp, thispsfn[i, :, m], label='Sample')
                if trueinfo and datatype == 'mock':
                    axis.plot(angldisptemp, truepsfn[i, :, m], label='Mock', color='g', ls='--')
                if exprtype == 'ferm':
                    axis.plot(angldisptemp, fermpsfn[i, :, m], label='Fermi-LAT', color='r', ls='-.', alpha=0.4)
                axis.set_yscale('log')
                if m == numbevtt - 1:
                    axis.set_xlabel(r'$\theta$ ' + strganglunit)
                if i == 0 and exprtype == 'ferm':
                    axis.set_ylabel(evttstrg[m])
                if m == 0:
                    axis.set_title(enerstrg[i])  
                if i == numbener - 1 and m == numbevtt - 1:
                    axis.legend(loc=2)
                indxsamp = indxsamppsfipara[i*nformpara+m*numbener*nformpara]
                if psfntype == 'singgaus':
                    strg = r'$\sigma = %.3g$ ' % rad2deg(thissampvarb[indxsamp]) + strganglunit
                elif psfntype == 'singking':
                    strg = r'$\sigma = %.3g$ ' % rad2deg(thissampvarb[indxsamp]) + strganglunit + '\n'
                    strg += r'$\gamma = %.3g$' % thissampvarb[indxsamp+1]
                elif psfntype == 'doubgaus':
                    strg = r'$f = %.3g$' % thissampvarb[indxsamp] + '\n'
                    if exprtype == 'sdss':
                        paratemp = rad2deg(thissampvarb[indxsamp+1]) * 3600.
                    if exprtype == 'ferm':
                        paratemp = rad2deg(thissampvarb[indxsamp+1])
                    strg += r'$\sigma = %.3g$ ' % paratemp + strganglunit + '\n'
                    if exprtype == 'sdss':
                        paratemp = rad2deg(thissampvarb[indxsamp+2]) * 3600.
                    if exprtype == 'ferm':
                        paratemp = rad2deg(thissampvarb[indxsamp+2])
                    strg += r'$\sigma = %.3g$ ' % paratemp + strganglunit
                elif psfntype == 'gausking':
                    strg = r'$f_G = %.3g$' % thissampvarb[indxsamp] + '\n'
                    strg += r'$\sigma_G = %.3g$ ' % rad2deg(thissampvarb[indxsamp+1]) + strganglunit + '\n'
                    strg += r'$\sigma_K = %.3g$ ' % rad2deg(thissampvarb[indxsamp+2]) + strganglunit + '\n'
                    strg += r'$\gamma = %.3g$' % thissampvarb[indxsamp+3]
                elif psfntype == 'doubking':
                    strg = r'$f_c = %.3g$' % thissampvarb[indxsamp] + '\n'
                    strg += r'$\sigma_c = %.3g$ ' % rad2deg(thissampvarb[indxsamp+1]) + strganglunit + '\n'
                    strg += r'$\gamma_c = %.3g$' % thissampvarb[indxsamp+2] + '\n'
                    strg += r'$\sigma_t = %.3g$ ' % rad2deg(thissampvarb[indxsamp+3]) + strganglunit + '\n'
                    strg += r'$\gamma_t = %.3g$' % thissampvarb[indxsamp+4]
                axis.text(0.75, 0.75, strg, va='center', ha='center', transform=axis.transAxes, fontsize=18)
                
                if exprtype == 'ferm':
                    axis.set_ylim([1e0, 1e6])
                if exprtype == 'sdss':
                    axis.set_ylim([1e7, 1e11])

        plt.savefig(plotpath + 'psfnprof_' + rtag + '_%09d.png' % j)
        plt.close(figr)
    
    
def plot_fwhm(thisfwhm):
    
    figr, axis = plt.subplots()

    tranfwhm = transpose(thisfwhm)
    imag = axis.imshow(rad2deg(tranfwhm), origin='lower', extent=[binsener[0], binsener[-1], 0, 4],                      cmap='BuPu', interpolation='none', alpha=0.4)
    plt.colorbar(imag, ax=axis, fraction=0.05)
    axis.set_xscale('log')
    axis.set_ylabel('PSF Class')
    axis.set_xlabel(r'$E_\gamma$ [GeV]')
    axis.set_yticks([0.5, 1.5, 2.5, 3.5])
    axis.set_yticklabels(['0', '1', '2', '3'])
    axis.set_xticks(binsener)
    axis.set_xticklabels(['%.2g' % binsener[i] for i in indxener])
    axis.set_title('PSF FWHM')
    for i in indxener:
        for m in indxevtt:
            axis.text(meanener[i], jevtt[m]+0.5, r'$%.3g^\circ$' % rad2deg(tranfwhm[m, i]), ha='center', va='center', fontsize=14)

    figr.subplots_adjust(bottom=0.2)
    plt.savefig(plotpath + 'fwhmcnts_' + rtag + '_%09d.png' % j)
    plt.close(figr)
    
    
def plot_backcntsmean(backcntsmean):
    
    figr, axis = plt.subplots()

    tranumbbackcntsrofimean = transpose(backcntsmean)
    
    imag = axis.imshow(tranumbbackcntsrofimean, origin='lower', extent=[binsener[0], binsener[-1], 0, 4],                      cmap='BuPu', interpolation='none', alpha=0.4)
    plt.colorbar(imag, ax=axis, fraction=0.05)
    axis.set_xscale('log')
    axis.set_ylabel('PSF Class')
    axis.set_xlabel(r'$E_\gamma$ [GeV]')
    axis.set_yticks([0.5, 1.5, 2.5, 3.5])
    axis.set_yticklabels(['0', '1', '2', '3'])
    axis.set_title('Mean FDM counts inside a PSF FWHM')
    for i in indxener:
        for m in indxevtt:
            axis.text(meanener[i], jevtt[m]+0.5, '%.3g' % tranumbbackcntsrofimean[m, i], ha='center', va='center')
            
    figr.subplots_adjust(bottom=0.2)
    plt.savefig(plotpath + 'backcnts_' + rtag + '_%09d.png' % j)
    plt.close(figr)


# In[161]:

def chsq_fdfnslop(para, i):

    fdfnslop = para[0]
    fdfnnormnorm = para[1]
    
    fluxhistmodl = fdfnnormnorm * diffspec[i, :] * pdfn_spec(meanspec[i, :], fdfnslop, minmspec[i], maxmspec[i])

    chsq = sum(((fluxhistmodl.flatten()[jspecfgl3] - fgl3spechist[i, jspecfgl3]) / fgl3spechist[i, jspecfgl3])**2)
    
    return chsq


# In[162]:

def retr_psfimodl(nformpara, exprtype, psfntype, numbener, numbevtt, jener, jevtt):
    
    if exprtype == 'ferm':
        strganglunit = '[deg]'
    if exprtype == 'sdss':
        strganglunit = '[arcsec]'

    numbpsfiparaevtt = nformpara * numbener
    
    minmformpara = zeros(nformpara)
    maxmformpara = zeros(nformpara)
    factformpara = zeros(nformpara)
    scalformpara = zeros(nformpara, dtype=object)
    if exprtype == 'ferm':
        minmanglpsfn = deg2rad(0.01)
        maxmanglpsfn = deg2rad(3.)
        minmgamm = 2.
        maxmgamm = 20.
        minmpsfnfrac = 0.
        maxmpsfnfrac = 1.
    if exprtype == 'sdss':
        minmanglpsfn = deg2rad(0.01 / 3600.)
        maxmanglpsfn = deg2rad(2. / 3600.)
    if psfntype == 'singgaus':
        minmformpara[0] = minmanglpsfn
        maxmformpara[0] = maxmanglpsfn
        scalformpara[0] = 'logt'
        strgformpara = [r'$\sigma']
    elif psfntype == 'singking':
        minmformpara[0] = minmanglpsfn
        maxmformpara[0] = maxmanglpsfn
        minmformpara[1] = minmgamm
        maxmformpara[1] = maxmgamm
        scalformpara[0] = 'logt'
        scalformpara[1] = 'atan'
        strgformpara = [r'$\sigma', r'$\gamma']
    elif psfntype == 'doubgaus':
        minmformpara[0] = minmpsfnfrac
        maxmformpara[0] = maxmpsfnfrac
        minmformpara[1] = minmanglpsfn
        maxmformpara[1] = maxmanglpsfn
        minmformpara[2] = minmanglpsfn
        maxmformpara[2] = maxmanglpsfn
        scalformpara[0] = 'self'
        scalformpara[1] = 'logt'
        scalformpara[2] = 'logt'
        strgformpara = ['$f_c', r'$\sigma_c', r'$\sigma_t']
    elif psfntype == 'gausking':
        minmformpara[0] = minmpsfnfrac
        maxmformpara[0] = maxmpsfnfrac
        minmformpara[1] = minmanglpsfn
        maxmformpara[1] = maxmanglpsfn
        minmformpara[2] = minmanglpsfn
        maxmformpara[2] = maxmanglpsfn
        minmformpara[3] = minmgamm
        maxmformpara[3] = maxmgamm
        scalformpara[0] = 'self'
        scalformpara[1] = 'logt'
        scalformpara[2] = 'logt'
        scalformpara[3] = 'atan'
        strgformpara = ['$f_g', r'$\sigma_g', r'$\sigma_k', r'$\gamma']
    elif psfntype == 'doubking':
        minmformpara[0] = minmpsfnfrac
        maxmformpara[0] = maxmpsfnfrac
        minmformpara[1] = minmanglpsfn
        maxmformpara[1] = maxmanglpsfn
        minmformpara[2] = minmgamm
        maxmformpara[2] = maxmgamm
        minmformpara[3] = minmanglpsfn
        maxmformpara[3] = maxmanglpsfn
        minmformpara[4] = minmgamm
        maxmformpara[4] = maxmgamm
        scalformpara[0] = 'self'
        scalformpara[1] = 'logt'
        scalformpara[2] = 'atan'
        scalformpara[3] = 'logt'
        scalformpara[4] = 'atan'
        strgformpara = ['$f_c', r'$\sigma_c', r'$\gamma_c', r'$\sigma_t', r'$\gamma_t']
    
    for k in range(nformpara):
        if scalformpara[k] == 'self':
            factformpara[k] = maxmformpara[k] - minmformpara[k]
        if scalformpara[k] == 'logt':
            factformpara[k] = log(maxmformpara[k] / minmformpara[k])
        if scalformpara[k] == 'atan':
            factformpara[k] = arctan(maxmformpara[k]) - arctan(minmformpara[k])
            
    minmpsfipara = tile(tile(minmformpara, numbener), numbevtt)
    maxmpsfipara = tile(tile(maxmformpara, numbener), numbevtt)
    scalpsfipara = tile(tile(scalformpara, numbener), numbevtt)
    factpsfipara = tile(tile(factformpara, numbener), numbevtt)
    
    indxener = arange(numbevtt)
    indxener = arange(numbener)
    strgpsfipara = [strgformpara[k] + '^{%d%d}$' % (jener[i], jevtt[m])                         for m in indxevtt for i in indxener for k in range(nformpara)]

    global jpsfiparainit
    jpsfiparainit = (arange(numbevtt)[:, None] * numbpsfiparaevtt + arange(numbener)[None, :] * nformpara).flatten()

    for k in range(jpsfiparainit.size):
        if psfntype == 'singgaus' or psfntype == 'singking':
            strgpsfipara[jpsfiparainit[k]] += ' ' + strganglunit
        elif psfntype == 'doubgaus' or psfntype == 'gausking':
            strgpsfipara[jpsfiparainit[k]+1] += ' ' + strganglunit
            strgpsfipara[jpsfiparainit[k]+2] += ' ' + strganglunit
        elif psfntype == 'doubking':
            strgpsfipara[jpsfiparainit[k]+1] += ' ' + strganglunit
            strgpsfipara[jpsfiparainit[k]+3] += ' ' + strganglunit

    
    return minmpsfipara, maxmpsfipara, factpsfipara, strgpsfipara, scalpsfipara, jpsfiparainit


# In[163]:

def retr_strgfluxunit(exprtype):
    
    if exprtype == 'ferm':
        strgfluxunit = r'[1/cm$^2$/s/GeV]'
    if exprtype == 'sdss':
        strgfluxunit = '[nMgy]'
        
    return strgfluxunit
             


# In[164]:

def retr_enerstrg(exprtype):
    if exprtype == 'ferm':
        binsenerstrg = []
        enerstrg = []
        for i in indxener:
            binsenerstrg.append('%.3g GeV - %.3g GeV' % (binsener[i], binsener[i+1]))
            enerstrg.append('%.3g GeV' % meanener[i])
    if exprtype == 'sdss':
        binsenerstrg = ['i-band', 'r-band', 'g-band']
        enerstrg = ['i-band', 'r-band', 'g-band']
        
    return enerstrg, binsenerstrg


# In[165]:

def make_anim():

    listname = ['errrcnts0A', 'datacnts0A', 'resicnts0A', 'modlcnts0A', 'histspec',         'scatspec', 'psfnprof', 'compfrac0', 'compfracspec', 'scatpixl']
    
    #print os.listdir(plotpath)
    for name in listname:
    
        

        
        strg = '%s*0.png' % name
        listfile = fnmatch.filter(os.listdir(plotpath), strg)[int(numbburn/plotperd):]
        
        print fnmatch.filter(os.listdir(plotpath), strg)
        print listfile

        nfile = len(listfile)
        jfile = choice(arange(nfile), replace=False, size=nfile)

        cmnd = 'convert -delay 20 '
        for k in range(nfile):
            cmnd += '%s ' % listfile[jfile[k]]
        cmnd += ' %s.gif' % name
        os.system(cmnd)



# In[166]:

def init(cnfg):
    
    timetotlreal = time.time()
    timetotlproc = time.clock()
    
    # temp
    #warnings.filterwarnings("ignore")
    
    # read the configuration dictionary
    global verbtype, plotperd, numbswep, numbburn, factthin, numbproc,         fracrand, colrprio, makeplot, diagsamp,         stdvfdfnnorm, stdvfdfnslop, stdvpsfipara, stdvback, stdvlbhl, stdvspec,         datatype, regitype, randinit, psfntype, exprtype,         pntscntr, numbpopl,         minmfdfnnorm, maxmfdfnnorm,         minmfdfnslop, maxmfdfnslop,         minmspec, maxmspec,         minmsind, maxmsind,         initnumbpnts, trueinfo, pixltype, nsidecart, nsideheal,         jener, jevtt, minmnumbpnts, maxmnumbpnts, probprop, maxmgang, liketype,         nsideheal, spmrlbhl, minmnormback, maxmnormback
        
    verbtype = cnfg['verbtype']
    plotperd = cnfg['plotperd']
    makeplot = cnfg['makeplot']
    diagsamp = cnfg['diagsamp']
    
    numbproc = cnfg['numbproc']
    numbswep = cnfg['numbswep']
    numbburn = cnfg['numbburn']
    factthin = cnfg['factthin']
    
    stdvfdfnnorm = cnfg['stdvfdfnnorm']
    stdvfdfnslop = cnfg['stdvfdfnslop']
    stdvpsfipara = cnfg['stdvpsfipara']
    stdvback = cnfg['stdvback']
    stdvlbhl = cnfg['stdvlbhl']
    stdvspec = cnfg['stdvspec']
    
    spmrlbhl = cnfg['spmrlbhl']
    
    fracrand = cnfg['fracrand']
    
    datatype = cnfg['datatype']
    
    if datatype == 'mock':
        mockpsfntype = cnfg['mockpsfntype']
    
    modlpsfntype = cnfg['modlpsfntype']
    
    liketype = cnfg['liketype']
    exprtype = cnfg['exprtype']
    pixltype = cnfg['pixltype']
    
    regitype = cnfg['regitype']
    randinit = cnfg['randinit']
    pntscntr = cnfg['pntscntr']

    colrprio = cnfg['colrprio']
    numbpopl = cnfg['numbpopl']
    jener = cnfg['jener']
    jevtt = cnfg['jevtt']
    
    maxmangleval = cnfg['maxmangleval']

    minmspec = cnfg['minmspec']
    maxmspec = cnfg['maxmspec']
    if colrprio:
        minmsind = cnfg['minmsind']
        maxmsind = cnfg['maxmsind']
    
    minmfdfnnorm = cnfg['minmfdfnnorm']
    maxmfdfnnorm = cnfg['maxmfdfnnorm']
    minmfdfnslop = cnfg['minmfdfnslop']
    maxmfdfnslop = cnfg['maxmfdfnslop']
    

    maxmnormback = cnfg['maxmnormback']
    minmnormback = cnfg['minmnormback']
    
    
    mockfdfnslop = cnfg['mockfdfnslop']
    mocknumbpnts = cnfg['mocknumbpnts']
    mockfdfnnorm = cnfg['mockfdfnnorm']
    mocknormback = cnfg['mocknormback']
    
    maxmnumbpnts = cnfg['maxmnumbpnts']
    
    probprop = cnfg['probprop']
    exprfluxstrg = cnfg['exprfluxstrg']
    listbackfluxstrg = cnfg['listbackfluxstrg']
    expostrg = cnfg['expostrg']
    initnumbpnts = cnfg['initnumbpnts']
    trueinfo = cnfg['trueinfo']
    
    margsize = cnfg['margsize']
    maxmgang = cnfg['maxmgang']
    lgalcntr = cnfg['lgalcntr']
    bgalcntr = cnfg['bgalcntr']
    

    nsideheal = cnfg['nsideheal']
    nsidecart = cnfg['nsidecart']
    
    if colrprio:
        if minmspec.size != 1 or minmspec.size != 1:
            print 'Spectral limits must be numpy scalars when color priors are used!'
            #return
        

    
    # the number of processes (each with numbswep samples)
    if numbproc == None:
        if os.uname()[1] == 'fink1.rc.fas.harvard.edu':
            numbproc = 10
        else:
            numbproc = 1
        
    # date and time
    global datetimestrg
    datetimestrg = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
    if verbtype > 0:
        print 'PNTS_TRAN started at ', datetimestrg
        print 'Initializing...'
    
    global strgfluxunit
    strgfluxunit = retr_strgfluxunit(exprtype)
        
    # number of bins
    global numbspec
    numbspec = 10
    
    global numbbins
    numbbins = 10
    
    if datatype == 'mock':
        mocknormback = mocknormback[:, jener]
        if not colrprio:
            mockfdfnslop = mockfdfnslop[:, jener]

    if not colrprio:
        minmspec = minmspec[jener]
        maxmspec = maxmspec[jener]
        
    
    
    global minmnumbpnts
    minmnumbpnts = 1

    global indxback, numbback
    numbback = len(listbackfluxstrg)
    indxback = arange(numbback)
    
    if numbback == 1:
        probprop[5] = 0.
        
    # PSF class axis
    global numbevtt, indxevtt
    numbevtt = jevtt.size
    indxevtt = arange(numbevtt)
    
    # energy axis
    global binsener, diffener, meanener, jenerbins, numbener, indxener
    numbener = jener.size
    jenerbins = empty(numbener+1, dtype=int)
    jenerbins[0:-1] = jener
    jenerbins[-1] = jener[-1] + 1
    binsener = array([0.1, 0.3, 1., 3., 10., 100.])[jenerbins]
    diffener = (roll(binsener, -1) - binsener)[0:-1]

    meanener = sqrt(roll(binsener, -1) * binsener)[0:-1]
    indxener = arange(numbener, dtype=int)
    
    global indxenerfdfn, enerfdfn
    if colrprio: 
        # temp
        indxenerfdfn = array([numbener / 2])
        f
        minmspec = minmspec * (meanener[indxenerfdfn] / meanener)**2
        maxmspec = maxmspec * (meanener[indxenerfdfn] / meanener)**2
        
        if datatype == 'mock':
            
            mockfdfnslop = tile(mockfdfnslop, (1, numbener))
        
    else:
        indxenerfdfn = indxener

    enerfdfn = meanener[indxenerfdfn]
        
    global indxenerprio
    if colrprio:
        indxenerprio = indxenerfdfn
    else:
        indxenerprio = indxener

    global indxspecpivt
    indxspecpivt = numbspec / 2
    
    # temp
    if exprtype == 'sdss':
        diffener = ones(numbener)
        
    # angular deviation
    global nangl, angl, devi, angldisp, maxmangldisp
    nangl = 100
    if exprtype == 'sdss':
        maxmangldisp = deg2rad(5. / 3600.) # [rad]
    if exprtype == 'ferm':
        maxmangldisp = deg2rad(5.) # [rad]
    angldisp = linspace(0., maxmangldisp, nangl) # [rad]
    maxmangl = deg2rad(3.5 * maxmgang) # [rad]
    angl = linspace(0., maxmangl, nangl) # [rad]

    
    global strganglunit
    if exprtype == 'ferm':
        strganglunit = '[deg]'
    if exprtype == 'sdss':
        strganglunit = '[arcsec]'
        
    if exprtype == 'ferm':
        global fermpsfn
        fermpsfn = retr_fermpsfn()




        
        
    # energy bin string
    global binsenerstrg, enerstrg
    enerstrg, binsenerstrg = retr_enerstrg(exprtype)
    
        
    # PSF class string
    global evttstrg
    evttstrg = []
    for m in indxevtt:
        evttstrg.append('PSF%d' % jevtt[m])
     
    global mrkralph
    mrkralph = 0.8
    
    global spltjcbnfact
    spltjcbnfact = log(2.**(2 - numbener))
    
    # number of components
    global numbcomp, jcomp, jcbnsplt, numbcompcolr
    numbcomp = 2 + numbener
    if colrprio:
        numbcomp += 1
    numbcompcolr = 4
    jcomp = arange(numbcomp)
    jcbnsplt = 2.**(2 - numbener)
    
    # limits on the number of point sources
    global factfdfnnorm
    factfdfnnorm = log(maxmfdfnnorm / minmfdfnnorm)
    

    
    # PSF parameters
    global nformpara
    if psfntype == 'singgaus':
        nformpara = 1
    elif psfntype == 'singking':
        nformpara = 2 
    elif psfntype == 'doubgaus':
        nformpara = 3
    elif psfntype == 'gausking':
        nformpara = 4
    elif psfntype == 'doubking':
        nformpara = 5

    global numbpsfiparaevtt, numbpsfipara, ipsfipara
    numbpsfiparaevtt = numbener * nformpara
    numbpsfipara = numbpsfiparaevtt * numbevtt
    ipsfipara = arange(numbpsfipara)   
    
    global longlabl, latilabl
    if regitype == 'igal':
        longlabl = '$l$'
        latilabl = '$b$'
    else:
        longlabl = r'$\nu$'
        latilabl = r'$\mu$'
        
    if exprtype == 'ferm':
        longlabl += r' [$^\circ$]'
        latilabl += r' [$^\circ$]'
    if exprtype == 'sdss':
        longlabl += ' [arcsec]'
        latilabl += ' [arcsec]'
        
    # factors in the prior expression
    global priofactlgalbgal, priofactfdfnslop, fdfnnormfact
    priofactlgalbgal = 2. * log(1. / 2. / maxmgang)
    priofactfdfnslop = numbener * log(1. / (arctan(maxmfdfnslop) - arctan(minmfdfnslop)))
    fdfnnormfact = log(1. / (log(maxmfdfnnorm) - log(minmfdfnnorm)))

    # sample vector indices
    global indxsampnumbpnts, indxsampfdfnnorm, indxsampfdfnslop, indxsamppsfipara, indxsampnormback  
    indxsampnumbpnts = arange(numbpopl)
    indxsampfdfnnorm = arange(numbpopl) + amax(indxsampnumbpnts) + 1
    indxsampfdfnslop = arange(numbpopl * numbener).reshape((numbpopl, numbener)) + amax(indxsampfdfnnorm) + 1
    indxsamppsfipara = arange(numbpsfipara) + amax(indxsampfdfnslop) + 1
    indxsampnormback = arange(numbback * numbener).reshape((numbback, numbener)) + amax(indxsamppsfipara) + 1
    
    global fluxpivt
    fluxpivt = sqrt(minmspec * maxmspec)
    
    global maxmnumbcomp, indxcompinit
    maxmnumbcomp = maxmnumbpnts * numbcomp
    indxcompinit = amax(indxsampnormback) + 1
    
    # maximum number of parameters
    global maxmsampsize
    maxmsampsize = indxcompinit + maxmnumbcomp * numbpopl
    
    if numbburn == None:
        numbburn = numbswep / 5
    if factthin == None:
        factthin = min(int(maxmsampsize) * 5, numbswep / 2)

        
    global strgprop
    strgprop = ['fdfnnorm', 'fdfnslop', 'psfipara', 'normback', 'brth',                 'deth', 'splt', 'merg', 'lgal', 'bgal', 'spec', 'sind']
    
    


    global indxpropfdfnnorm, indxpropfdfnslop, indxproppsfipara, indxpropnormback,         indxpropbrth, indxpropdeth, indxpropsplt, indxpropmerg,         indxproplgal, indxpropbgal, indxpropspec, indxpropsind
    indxpropfdfnnorm = 0
    indxpropfdfnslop = 1
    indxproppsfipara = 2
    indxpropnormback = 3
    indxpropbrth = 4
    indxpropdeth = 5
    indxpropsplt = 6
    indxpropmerg = 7
    indxproplgal = 8
    indxpropbgal = 9
    indxpropspec = 10
    indxpropsind = 11

    if probprop == None:

        probfdfnnorm = array([1.])
        if colrprio:
            probfdfnslop = array([1.])
        else:
            #probfdfnslop = array([1.] * numbener)
            probfdfnslop = array([1.])
            
        #probpsfipara = array([1.] * numbpsfipara)
        #probnormback = array([1.] * numbback * numbener)
        
        probpsfipara = array([1.])
        probnormback = array([1.])
        
        probbrth = array([0.1 * sum(maxmnumbpnts)])
        probdeth = array([0.1 * sum(maxmnumbpnts)])
        probsplt = array([0. * sum(maxmnumbpnts)])
        probmerg = array([0. * sum(maxmnumbpnts)])
        
        problgal = array([sum(maxmnumbpnts) / 2.])
        probbgal = array([sum(maxmnumbpnts) / 2.])
        if colrprio:
            probspec = array([sum(maxmnumbpnts) / 2.])
            probsind = array([sum(maxmnumbpnts) / 2.])
        else:
            probspec = array([sum(maxmnumbpnts) / 2.])
            #probspec = array([sum(maxmnumbpnts) / 2.] * numbener)
            probsind = array([0.])
            
                            
        probprop = concatenate((probfdfnnorm, probfdfnslop,                                 probpsfipara, probnormback,                                 probbrth, probdeth,                                 probsplt, probmerg,                                 problgal, probbgal,                                 probspec, probsind))
        

        probprop /= sum(probprop)
        

        

    # number of proposal types
    global numbprop
    numbprop = probprop.size
   
    if verbtype > 1:
        print 'probprop: '
        print vstack((arange(numbprop), strgprop, probprop)).T


    # run tag
    global rtag
    rtag = retr_rtag(None)
    
    # plots
    if makeplot:
        global plotpath
        if os.uname()[1] == 'fink1.rc.fas.harvard.edu' and getpass.getuser() == 'tansu':
            plotfold = '/n/pan/www/tansu/png/pnts_tran/'
        else:
            plotfold = os.environ["PNTS_TRAN_DATA_PATH"] + '/png/'
        plotpath = plotfold + datetimestrg + '_' + rtag + '/'
        cmnd = 'mkdir -p ' + plotpath
        os.system(cmnd)


        
    global factfdfnslop
    factfdfnslop = arctan(maxmfdfnslop) - arctan(minmfdfnslop)
    
    if colrprio:
        global factsind
        factsind = arctan(maxmsind) - arctan(minmsind)


    # number of samples to be saved
    global numbsamp
    numbsamp = (numbswep - numbburn) / factthin

    # rescale the positional update scale
    stdvlbhl /= 2. * maxmgang

    

    
    # determine proposal probabilities  
    global probpropminm, probpropmaxm
    probpropminm = copy(probprop)
    probpropmaxm = copy(probprop)
    probpropminm[[indxpropdeth, indxpropmerg]] = 0.
    probpropmaxm[[indxpropbrth, indxpropsplt]] = 0.
    
    global prop
    prop = arange(probprop.size)
    probprop /= sum(probprop)
    probpropmaxm /= sum(probpropmaxm)
    probpropminm /= sum(probpropminm)
    

    # population indices
    global indxpopl
    indxpopl = arange(numbpopl)
        
    global maxmgangmarg
    maxmgangmarg = maxmgang + margsize
    
    global minmlgal, maxmlgal, minmbgal, maxmbgal, minmlgalrofi, maxmlgalmarg, minmbgalmarg, maxmbgalmarg
    minmlgalmarg = -maxmgangmarg
    maxmlgalmarg = maxmgangmarg
    minmbgalmarg = -maxmgangmarg
    maxmbgalmarg = maxmgangmarg
    minmlgal = -maxmgang
    maxmlgal = maxmgang
    minmbgal = -maxmgang
    maxmbgal = maxmgang
    

    # input data
    global npixlheal
    if datatype == 'inpt':
        
        path = os.environ["PNTS_TRAN_DATA_PATH"] + '/' + exprfluxstrg
        exprflux = pf.getdata(path)

        jenerfull = arange(exprflux.shape[0])
        jevttfull = arange(exprflux.shape[2])

        if pixltype == 'heal':
            npixlheal = exprflux.shape[1]
            nsideheal = int(sqrt(npixlheal / 12))
        else:
            nsidecart = exprflux.shape[1]
            exprflux = exprflux.reshape((exprflux.shape[0], nsidecart**2, exprflux.shape[3]))
            
    else:
        
        if exprtype == 'ferm':
            jenerfull = arange(5)
            jevttfull = arange(4)
         


    
    global apix
    if pixltype == 'heal':
        npixlheal = nsideheal**2 * 12
        apix = 4. * pi / npixlheal
    if pixltype == 'cart':
        global binslgalcart, binsbgalcart, lgalcart, bgalcart
        binslgalcart = linspace(minmlgal, maxmlgal, nsidecart + 1)
        binsbgalcart = linspace(minmbgal, maxmbgal, nsidecart + 1)
        lgalcart = (binslgalcart[0:-1] + binslgalcart[1:]) / 2.
        bgalcart = (binsbgalcart[0:-1] + binsbgalcart[1:]) / 2.
        apix = deg2rad(2. * maxmgang / nsidecart)**2
        
    # temp
    global tracsamp
    tracsamp = False
    

    
    global cntrlghp, cntrbghp
    if regitype == 'igal':
        cntrlghp, cntrbghp = 0., 0.
    else:
        cntrlghp, cntrbghp = 0., 90.
    
    # marker size for count map plots
    global minmmrkrsize, maxmmrkrsize
    minmmrkrsize = 50
    maxmmrkrsize = 500
    
    ## FDM normalization prior limits
    global factnormback
    factnormback = log(maxmnormback / minmnormback)

    # sky coordinates
    global binslbhl
    binslbhl = linspace(-maxmgang, maxmgang, numbbins + 1)
    

    global binsspec, meanspec, diffspec
    binsspec = zeros((numbener, numbspec + 1))
    for i in indxener:
        binsspec[i, :] = logspace(log10(minmspec[i]), log10(maxmspec[i]), numbspec + 1)
    meanspec = sqrt(binsspec[:, 1:] * binsspec[:, 0:-1])
    diffspec = binsspec[:, 1:] - binsspec[:, 0:-1]

    if colrprio:
        global binssind, meansind, diffsind
        binssindunit = arange(numbbins + 1.) / numbbins
        meansindunit = (binssindunit[:-1] + binssindunit[1:]) / 2.
        binssind = icdf_atan(binssindunit, minmsind, factsind)
        meansind = icdf_atan(meansindunit, minmsind, factsind)
        diffsind = binssind[1:] - binssind[:-1]


    
    global meanspecprox, numbspecprox
    # temp
    numbspecprox = 1
    meanspecprox = binsspec[indxenerfdfn, numbspec / 2]
    



    global minmpsfipara, maxmpsfipara, factpsfipara, strgpsfipara, scalpsfipara
    minmpsfipara, maxmpsfipara, factpsfipara,         strgpsfipara, scalpsfipara, jpsfiparainit = retr_psfimodl(nformpara, exprtype,                                                                   psfntype, numbener, numbevtt, jener, jevtt)


    
 
    if verbtype > 1:
        print 'indxsampnumbpnts: ', indxsampnumbpnts
        print 'indxsampfdfnnorm: ', indxsampfdfnnorm
        print 'indxsampfdfnslop: ', indxsampfdfnslop
        print 'indxsamppsfipara: ', indxsamppsfipara
        print 'indxsampnormback: '
        print indxsampnormback
        print 'indxcompinit: ', indxcompinit

    ## roi parameters for healpy visualization tools

    global extt, frambndr, frambndrmarg
    extt = [minmlgal, maxmlgal, minmbgal, maxmbgal]
    if exprtype == 'sdss':
        extt *= 3600.
        frambndr = maxmgang * 3600.
        frambndrmarg = maxmgangmarg * 3600.
    else:
        frambndr = maxmgang
        frambndrmarg = maxmgangmarg
      

    
    # region of interest
    global lgalgrid, bgalgrid
    if pixltype == 'heal':
        
        global jpixlrofi
        lgalheal, bgalheal, nsideheal, npixlheal, apix = tdpy_util.retr_heal(nsideheal)


        jpixlrofi = where((abs(lgalheal) < maxmgang) & (abs(bgalheal) < maxmgang))[0]
        jpixlrofimarg = where((abs(lgalheal) < maxmgangmarg + 300. / nsideheal) &                               (abs(bgalheal) < maxmgangmarg + 300. / nsideheal))[0]

        
        lgalgrid = lgalheal[jpixlrofi]
        bgalgrid = bgalheal[jpixlrofi]
        
        global pixlcnvt
        path = os.environ["PNTS_TRAN_DATA_PATH"] + '/pixlcnvt_%03d.p' % maxmgang
        if os.path.isfile(path):
            fobj = open(path, 'rb')
            pixlcnvt = cPickle.load(fobj)
            fobj.close()
        else:
            pixlcnvt = zeros(npixlheal, dtype=int)
            for k in range(jpixlrofimarg.size):
                dist = retr_dist(lgalheal[jpixlrofimarg[k]], bgalheal[jpixlrofimarg[k]], lgalgrid, bgalgrid)
                pixlcnvt[jpixlrofimarg[k]] = argmin(dist)

            fobj = open(path, 'wb')
            cPickle.dump(pixlcnvt, fobj, protocol=cPickle.HIGHEST_PROTOCOL)
            fobj.close()


            
    else:
        isidecart = arange(nsidecart)
        temp = meshgrid(isidecart, isidecart, indexing='ij')
        bgalgrid = bgalcart[temp[1].flatten()]
        lgalgrid = lgalcart[temp[0].flatten()]
        
    global npixl, ipixl, fullindx
    npixl = lgalgrid.size
    ipixl = arange(npixl)
    fullindx = meshgrid(indxener, ipixl, indxevtt, indexing='ij')
    
    global filtindx
    filtindx = meshgrid(jener, ipixl, jevtt, indexing='ij')
    
    global gpixl, ngpixl
    ngpixl = 1000
    gpixl = choice(arange(npixl), size=ngpixl)


    if pixltype == 'heal':
        healindx = meshgrid(jenerfull, jpixlrofi, jevttfull, indexing='ij')
        

    if datatype == 'inpt' and pixltype == 'heal':
        exprflux = exprflux[healindx]


    if datatype == 'inpt':
        exprflux = exprflux[filtindx]


    # temp
    global truepsfipara
    if exprtype == 'ferm':
        
        if psfntype == 'singgaus':
            jfermformpara = array([1])
        elif psfntype == 'singking':
            jfermformpara = array([1, 2])
        elif psfntype == 'doubgaus':
            jfermformpara = array([0, 1, 3])
        elif psfntype == 'gausking':
            jfermformpara = array([0, 1, 3, 4])
        elif psfntype == 'doubking':
            jfermformpara = arange(5)

        jfermpsfipara = tile(jfermformpara, numbener) + repeat(indxener, jfermformpara.size) * nfermformpara
        jfermpsfipara = tile(jfermpsfipara, numbevtt) + repeat(indxevtt, jfermpsfipara.size) * numbener * nfermformpara

        truepsfipara = fermpsfipara[jfermpsfipara]
        
    else:   
        
        truepsfipara = None

    # temp
    truepsfipara = array([1., deg2rad(0.1), deg2rad(2.), 10.,                           1., deg2rad(0.1), deg2rad(2.), 10.,                           1., deg2rad(0.1), deg2rad(2.), 10.,                           1., deg2rad(0.1), deg2rad(2.), 10.,                           1., deg2rad(0.1), deg2rad(2.), 10.])

    print 'truepsfipara'
    print truepsfipara
    
    # exposure
    global expo
    if expostrg == 'unit':
        expo = ones((numbener, npixl, numbevtt))
    else:
        path = os.environ["PNTS_TRAN_DATA_PATH"] + '/' + expostrg
        expo = pf.getdata(path)

        if pixltype == 'heal':
            expo = expo[healindx]
        else:
            expo = expo.reshape((expo.shape[0], -1, expo.shape[-1]))
            
        expo = expo[filtindx]
    

    # backgrounds
    global backflux, backfluxmean
    backflux = []
    backfluxmean = []
    for c, backfluxstrg in enumerate(listbackfluxstrg):
        path = os.environ["PNTS_TRAN_DATA_PATH"] + '/' + backfluxstrg
        backfluxtemp = pf.getdata(path)
        if pixltype == 'heal':
            backfluxtemp = backfluxtemp[healindx]
        else:
            backfluxtemp = backfluxtemp.reshape((backfluxtemp.shape[0], -1, backfluxtemp.shape[-1]))
        backfluxtemp = backfluxtemp[filtindx]
        backflux.append(backfluxtemp)
        backfluxmean.append(mean(sum(backfluxtemp * expo, 2) / sum(expo, 2), 1))
        

        
    # test plot
    # temp
    if datatype == 'inpt' and makeplot and False:
        for i in indxener:
            for m in indxevtt:
                backfluxtemp = zeros(npixl)
                for c in indxback:
                    backfluxtemp[:] += backflux[c][i, :, m]
                resicnts = (exprflux[i, :, m] - backfluxtemp) * expo[i, :, m] * apix * diffener[i]

                
                resicntstemp = tdpy_util.retr_cart(resicnts, jpixlrofi=jpixlrofi, nsideinpt=nsideheal,                                                    minmlgal=minmlgal, maxmlgal=maxmlgal,                                                    minmbgal=minmbgal, maxmbgal=maxmbgal)
                figr, axis = plt.subplots()
                imag = axis.imshow(resicntstemp, origin='lower', cmap='RdGy', extent=extt)
                cbar = plt.colorbar(imag, ax=axis, fraction=0.05)
                plt.savefig(plotpath + 'testresiflux%d%d_' % (i, m) + rtag + '.png')
                plt.close(figr)
                
                cart = tdpy_util.retr_cart(exprflux[i, :, m], jpixlrofi=jpixlrofi, nsideinpt=nsideheal,                                                    minmlgal=minmlgal, maxmlgal=maxmlgal,                                                    minmbgal=minmbgal, maxmbgal=maxmbgal)
                figr, axis = plt.subplots()
                imag = axis.imshow(cart, origin='lower', cmap='RdGy', extent=extt)
                cbar = plt.colorbar(imag, ax=axis, fraction=0.05)
                plt.savefig(plotpath + 'testexprflux%d%d_' % (i, m) + rtag + '.png')
                plt.close(figr)
                
                cart = tdpy_util.retr_cart(backfluxtemp, jpixlrofi=jpixlrofi, nsideinpt=nsideheal,                                                    minmlgal=minmlgal, maxmlgal=maxmlgal,                                                    minmbgal=minmbgal, maxmbgal=maxmbgal)
                figr, axis = plt.subplots()
                imag = axis.imshow(cart, origin='lower', cmap='RdGy', extent=extt)
                cbar = plt.colorbar(imag, ax=axis, fraction=0.05)
                plt.savefig(plotpath + 'testbackflux%d%d_' % (i, m) + rtag + '.png')
                plt.close(figr)

                cart = tdpy_util.retr_cart(expo[i, :, m], jpixlrofi=jpixlrofi, nsideinpt=nsideheal,                                                    minmlgal=minmlgal, maxmlgal=maxmlgal,                                                    minmbgal=minmbgal, maxmbgal=maxmbgal)
                figr, axis = plt.subplots()
                imag = axis.imshow(cart, origin='lower', cmap='RdGy', extent=extt)
                cbar = plt.colorbar(imag, ax=axis, fraction=0.05)
                plt.savefig(plotpath + 'testexpo%d%d_' % (i, m) + rtag + '.png')
                plt.close(figr)
                
                
                
    # get 3FGL catalog
    if exprtype == 'ferm':
        global fgl3lgal, fgl3bgal, fgl3spec, indxfgl3rofi,             fgl3cnts, fgl3numbpnts, indxfgl3timevari, fgl3timevari, fgl3sind, fgl3spectype, fgl3scur, fgl3scut
        fgl3lgal, fgl3bgal, fgl3spec, fgl3gang,             fgl3cnts, fgl3timevari, fgl3sind, fgl3spectype, fgl3scur, fgl3scut = retr_fgl3()
        
        if regitype == 'ngal':
            rttr = hp.rotator.Rotator(rot=[0., 90., 0.], deg=True)
            fgl3bgal, fgl3lgal = rad2deg(rttr(deg2rad(90. - fgl3bgal), deg2rad(fgl3lgal)))
            fgl3bgal = 90. - fgl3bgal

        indxfgl3rofi = arange(fgl3lgal.size, dtype=int)
        for i in indxener:
            indxfgl3rofi = intersect1d(where((fgl3spec[0, i, :] > minmspec[i]) & (fgl3spec[0, i, :] < maxmspec[i]))[0], indxfgl3rofi)
        indxfgl3rofi = intersect1d(where((abs(fgl3lgal) < maxmgangmarg) & (abs(fgl3bgal) < maxmgangmarg))[0], indxfgl3rofi)

        indxfgl3timevari = where(fgl3timevari > 72.44)[0]
        

        plot_fgl3()
        
        fgl3lgal = fgl3lgal[indxfgl3rofi]
        fgl3bgal = fgl3bgal[indxfgl3rofi]
        fgl3spec = fgl3spec[:, :, indxfgl3rofi]
        fgl3cnts = fgl3cnts[:, indxfgl3rofi, :]
        fgl3spectype = fgl3spectype[indxfgl3rofi]
        fgl3scur = fgl3scur[indxfgl3rofi]
        fgl3scut = fgl3scut[indxfgl3rofi]
        fgl3timevari = fgl3timevari[indxfgl3rofi]

        indxfgl3timevari = where(fgl3timevari > 72.44)[0]

        fgl3numbpnts = fgl3lgal.size
        
        for i in indxener:
            if (fgl3spec[0, i, :] > maxmspec[i]).any():
                print 'maxmspec %d is bad!' % i


    # true data
    global truenumbpnts, truelgal, truebgal, truespec, truesind, truefdfnnorm, truefdfnslop, truenormback
    global truecnts, truesigm, jtruepntstimevari

    if datatype == 'inpt':
        truenumbpnts = None
        truefdfnnorm = None
        truefdfnslop = None
        truenormback = None
    
    
    # get count data
    global datacnts
    
    # input data
    if datatype == 'inpt':
        datacnts = exprflux * expo * apix * diffener[:, None, None] # [1]




    # mock data
    if datatype == 'mock':

        if mocknumbpnts == None:
            mocknumbpnts = empty(numbpopl)
            for l in indxpopl:
                mocknumbpnts[l] = random_integers(minmnumbpnts, maxmnumbpnts[l])
        
        mockindxpntsfull = []    
        for l in indxpopl:
            mockindxpntsfull.append(range(mocknumbpnts[l]))
          
        global mocksamp, mockindxsamplgal, mockindxsampbgal, mockindxsampspec, mockindxsampsind, mockindxsampcomp
        mockindxsamplgal, mockindxsampbgal, mockindxsampspec, mockindxsampsind, mockindxsampcomp = retr_indx(mockindxpntsfull)

        mocksamp = zeros(maxmsampsize)
        mocksamp[indxsampnumbpnts] = mocknumbpnts

        if mockfdfnnorm != None:
            mocksamp[indxsampfdfnnorm] = cdfn_logt(mockfdfnnorm, minmfdfnnorm, factfdfnnorm)
        else:
            mocksamp[indxsampfdfnnorm] = rand(numbener)
        
            
        if mockfdfnslop != None:
            mocksamp[indxsampfdfnslop] = cdfn_atan(mockfdfnslop, minmfdfnslop, factfdfnslop)
        else:
            mocksamp[indxsampfdfnslop] = rand(numbener)
            
            
        if truepsfipara != None: 
            for k in ipsfipara:
                if exprtype == 'ferm':
                    mocksamp[indxsamppsfipara[k]] = cdfn_psfipara(truepsfipara[k], k)
        else:
            mocksamp[indxsamppsfipara] = rand(numbpsfipara)
            
        for c in indxback:
            mocksamp[indxsampnormback[c, :]] = cdfn_logt(mocknormback[c, :], minmnormback[c], factnormback[c])

        if pntscntr:
            for l in indxpopl:
                mocksamp[mockindxsampcomp[l]] = 0.5
        else:
            for l in indxpopl:
                mocksamp[mockindxsampcomp[l]] = rand(mockindxsampcomp[l].size)

        if verbtype > 1:
            print 'mocksamp: '
            for k in range(mocksamp.size):
                print mocksamp[k]
            print
            
        
        global mocksampvarb, mockpntsfluxrofi
        mocksampvarb, mockppixl, mockcnts, mockpntsflux, mocktotlflux, mocktotlcnts = pars_samp(mockindxpntsfull, mocksamp)

        datacnts = zeros((numbener, npixl, numbevtt))
        for i in indxener:
            for k in range(npixl):
                for m in indxevtt:
                    datacnts[i, k, m] = poisson(mocktotlcnts[i, k, m])
              
        if trueinfo:
            
            truelgal = []
            truebgal = []
            truespec = []
            if colrprio:
                truesind = []

            for i in indxpopl:
                truelgal.append(mocksampvarb[mockindxsamplgal[l]])
                truebgal.append(mocksampvarb[mockindxsampbgal[l]])
                if colrprio:
                    truesind.append(mocksampvarb[mockindxsampsind[l]])
                    
            jtruepntstimevari = [array([])] * numbpopl
                    
            truenumbpnts = mocknumbpnts
            truefdfnnorm = mockfdfnnorm
            truefdfnslop = mockfdfnslop
            truenormback = mocknormback
            truecnts = mockcnts
            
            truespec = []
            for l in indxpopl:
                truespectemp = empty((3, numbener, mocknumbpnts[l]))
                truespectemp[:] = mocksampvarb[mockindxsampspec[l][None, :, :]]
                truespec.append(truespectemp)
                

        #plot_pntsdiff()
         
    #plot_datacntshist()
    

    if amax(abs(datacnts - datacnts.astype(int)) / datacnts) > 1e-3:
        print 'Fractional counts!'
        
    if amin(datacnts) < 0.:
        print 'Negative counts!'
        
    # temp
    #datacnts[where(datacnts < 0.)] = 0.
    
    global minmcnts, maxmcnts, binscnts
    expotemp = mean(expo, 1)
    minmcnts = minmspec * amin(expotemp, 1) * diffener
    maxmcnts = maxmspec * amax(expotemp, 1) * diffener

    binscnts = zeros((numbener, numbspec + 1))
    for i in indxener:
        binscnts[i, :] = logspace(log10(minmcnts[i]), log10(maxmcnts[i]), numbspec + 1) # [1]
        
    if trueinfo:
        global truelabl
        if datatype == 'mock':
            truelabl = 'Mock data'
        else:
            truelabl = '3FGL'
            
    ## Real data
    if datatype == 'inpt':
        if trueinfo:
            truenumbpnts = array([fgl3numbpnts], dtype=int)
            truelgal = [fgl3lgal]
            truebgal = [fgl3bgal]
            truespec = [fgl3spec]
            if colrprio:
                truesind = [fgl3sind]
            truecnts = [fgl3spec[0, :, :, None] * expo[:, retr_pixl(truebgal[0], truelgal[0]), :] *                             diffener[:, None, None]]
            jtruepntstimevari = [indxfgl3timevari]
            if exprtype == 'ferm':
                truespec = [fgl3spec]
                
    if trueinfo:
        global truepsfn
        if datatype == 'mock':
            truepsfn = retr_psfn(truepsfipara, indxener, angldisp, psfntype=psfntype)
        else:
            if exprtype == 'ferm':
                truepsfn = fermpsfn
            if exprtype == 'sdss':
                truepsfn = sdsspsfn
                
        truefwhm = retr_fwhm(truepsfn)
        
        truebackcnts = []
        truesigm = []
        for l in indxpopl:
            ppixl = retr_pixl(truebgal[l], truelgal[l])
            truebackcntstemp = zeros((numbener, truenumbpnts[l], numbevtt))
            for c in indxback:
                truebackcntstemp += backflux[c][:, ppixl, :] * expo[:, ppixl, :] *                                 diffener[:, None, None] * pi * truefwhm[:, None, :]**2 / 4.
            truebackcnts.append(truebackcntstemp)
            truesigm.append(truecnts[l] / sqrt(truebackcntstemp))
        
        if verbtype > 1:
            print 'truelgal: ', truelgal
            print 'truebgal: ', truebgal
            print 'truespec: '
            print truespec
            print 'truenumbpnts: ', truenumbpnts
            print 'truefdfnnorm: ', truefdfnnorm
            print 'truefdfnslop: ', truefdfnslop
            print 'truenormback: '
            print truenormback
            print
        
        
    global datafluxmean
    datafluxmean = mean(sum(datacnts, 2) / sum(expo, 2), 1) / apix / diffener
    
    global datacntssatu, resicntssatu
    datacntsmaxmtemp = amax(sum(datacnts, 2), 1)
    datacntsmean = mean(sum(datacnts, 2), 1)
    datacntssatu = ceil((datacntsmaxmtemp - datacntsmean) * 0.05 + datacntsmean)
    resicntssatu = ceil(datacntssatu * 0.5)
    
    # temp
    #datacntssatu = array([37., 28., 16.])

    # auxiliary variables for plots
    global datacntscart
    if pixltype == 'heal':
        for i in indxener:
            for m in indxevtt:
                datacntscarttemp = tdpy_util.retr_cart(datacnts[i, :, m], jpixlrofi=jpixlrofi, nsideinpt=nsideheal, minmlgal=minmlgal,                                                        maxmlgal=maxmlgal, minmbgal=minmbgal, maxmbgal=maxmbgal)
                if i == 0 and m == 0:
                    datacntscart = zeros((datacntscarttemp.shape[0], datacntscarttemp.shape[1], numbener, numbevtt))
                datacntscart[:, :, i, m] = datacntscarttemp
        
    else:
        datacntscart = datacnts.reshape((numbener, nsidecart, nsidecart, numbevtt))
        datacntscart = swapaxes(swapaxes(datacntscart, 0, 2), 0, 1)

    for i in indxener:
        jdatacntscart = where(datacntscart[:, :, i, :] > datacntssatu[i])
        datacntscart[jdatacntscart[0], jdatacntscart[1], i, jdatacntscart[2]] = datacntssatu[i]

    # make a look-up table of nearby pixels for each pixel
    global ypixl
    path = os.environ["PNTS_TRAN_DATA_PATH"] + '/ypixl_%03d.p' % maxmgang
    if os.path.isfile(path):
        fobj = open(path, 'rb')
        ypixl = cPickle.load(fobj)
        fobj.close()
    else:
        ypixl = [[] for h in range(numbspecprox)]
        for j in ipixl:
            dist = retr_dist(lgalgrid[j], bgalgrid[j], lgalgrid, bgalgrid)
            for h in range(numbspecprox):
                # temp
                ypixltemp = where(dist < deg2rad(maxmangleval))[0]
                ypixl[h].append(ypixltemp)
        fobj = open(path, 'wb')
        cPickle.dump(ypixl, fobj, protocol=cPickle.HIGHEST_PROTOCOL)
        fobj.close()


    # temp
    #plot_3fgl_thrs()
    #plot_intr()
    #plot_king()
    #plot_look()
    
    if verbtype > 0:
        print 'Sampling...'
    
    timereal = zeros(numbproc)
    timeproc = zeros(numbproc)
    if numbproc == 1:
        gridchan = [main(0)]
        
    else:

        if verbtype > 0:
            print 'Forking the sampler...'

        # process lock for simultaneous plotting
        global lock
        lock = mp.Lock()

        # process pool
        pool = mp.Pool(numbproc)
        
        # spawn the processes
        gridchan = pool.map(main, range(numbproc))
        
        pool.close()
        pool.join()

    for k in range(numbproc):
        timereal[k] = gridchan[k][17]
        timeproc[k] = gridchan[k][18]


    if verbtype > 0:
        print 'Accumulating samples from all processes...'
        tim0 = time.time()

    # parse the sample bundle
    listsampvarb = zeros((numbsamp, numbproc, maxmsampsize))
    listindxprop = zeros((numbswep, numbproc))
    listchro = zeros((numbswep, numbproc, 4))
    listllik = zeros((numbsamp, numbproc))
    listlpri = zeros((numbsamp, numbproc))
    listaccp = zeros((numbswep, numbproc))
    listmodlcnts = zeros((numbsamp, numbproc, ngpixl))
    listpntsfluxmean = zeros((numbsamp, numbproc, numbener))
    listindxpntsfull = []
    listindxsampmodi = zeros((numbswep, numbproc), dtype=int)
    
    listauxipara = empty((numbswep, numbproc, numbcomp))
    listlaccfrac = empty((numbswep, numbproc))
    listnumbpair = empty((numbswep, numbproc))
    listjcbnfact = empty((numbswep, numbproc))
    listcombfact = empty((numbswep, numbproc))

    levi = 0.
    info = 0.
    
    for k in range(numbproc):
        rtag = retr_rtag(k)
        listchan = gridchan[k]
        listsampvarb[:, k, :] = listchan[0]
        listindxprop[:, k] = listchan[1]
        listchro[:, k, :] = listchan[2]
        listllik[:, k] = listchan[3]
        listlpri[:, k] = listchan[4]
        listaccp[:, k] = listchan[5]
        listmodlcnts[:, k, :] = listchan[6]    
        listindxpntsfull.append(listchan[7])
        listindxsampmodi[:, k] = listchan[8]
        listauxipara[:, k, :] = listchan[9]
        listlaccfrac[:, k] = listchan[10]
        listnumbpair[:, k] = listchan[11]
        listjcbnfact[:, k] = listchan[12]
        listcombfact[:, k] = listchan[13]
        levi += listchan[14]
        info += listchan[15]
        listpntsfluxmean[:, k, :] = listchan[16]

    listindxprop = listindxprop.flatten()
    listauxipara = listauxipara.reshape((numbswep * numbproc, numbcomp))
    listlaccfrac = listlaccfrac.reshape(numbswep * numbproc)
    listnumbpair = listnumbpair.reshape(numbswep * numbproc)
    listjcbnfact = listjcbnfact.reshape(numbswep * numbproc)
    listcombfact = listcombfact.reshape(numbswep * numbproc)
    
    listchro = listchro.reshape((numbproc * numbswep, 4)) 
    listaccp = listaccp.flatten()
    listindxsampmodi = listindxsampmodi.flatten()
    
    
    
    rtag = retr_rtag(None)

    listnumbpnts = listsampvarb[:, :, indxsampnumbpnts].astype(int).reshape(numbsamp * numbproc, -1)
    listfdfnnorm = listsampvarb[:, :, indxsampfdfnnorm].reshape(numbsamp * numbproc, -1)
    listfdfnslop = listsampvarb[:, :, indxsampfdfnslop].reshape(numbsamp * numbproc, numbpopl, numbener)
    listpsfipara = listsampvarb[:, :, indxsamppsfipara].reshape(numbsamp * numbproc, -1)
    listnormback = listsampvarb[:, :, indxsampnormback].reshape(numbsamp * numbproc, numbback, numbener)
    
    listpntsfluxmean = listpntsfluxmean.reshape(numbsamp * numbproc, numbener)
    
    listlgal = [[] for l in indxpopl]
    listbgal = [[] for l in indxpopl]
    listspec = [[] for l in indxpopl]
    if colrprio:
        listsind = [[] for l in indxpopl]
    listspechist = empty((numbsamp * numbproc, numbpopl, numbener, numbspec))
    for k in range(numbproc):
        for j in range(numbsamp):            
            n = k * numbsamp + j
            indxsamplgal, indxsampbgal, indxsampspec, indxsampsind, indxsampcomp = retr_indx(listindxpntsfull[k][j])
            for l in indxpopl:
                listlgal[l].append(listsampvarb[j, k, indxsamplgal[l]])
                listbgal[l].append(listsampvarb[j, k, indxsampbgal[l]])
                listspec[l].append(listsampvarb[j, k, indxsampspec[l]])
                if colrprio:
                    listsind[l].append(listsampvarb[j, k, indxsampsind[l]])
                for i in indxener:
                    listspechist[n, l, i, :] = histogram(listspec[l][n][i, :], binsspec[i, :])[0]
        
    
    for l in indxpopl:
        
        listlgaltemp = zeros((numbsamp, maxmnumbpnts[l])) - 1.
        listbgaltemp = zeros((numbsamp, maxmnumbpnts[l])) - 1.
        listspectemp = zeros((numbsamp, numbener, maxmnumbpnts[l])) - 1.
        for k in range(numbsamp):
            listlgaltemp[k, 0:listlgal[l][k].size] = listlgal[l][k]
            listbgaltemp[k, 0:listbgal[l][k].size] = listbgal[l][k]
            listspectemp[k, :, 0:listspec[l][k].shape[1]] = listspec[l][k]

        listlgal[l] = listlgaltemp
        listbgal[l] = listbgaltemp 
        listspec[l] = listspectemp    

        
        
    if verbtype > 0:
        print 'Binning the probabilistic catalog...'
        tim0 = time.time()

    # posterior maps
    pntsprob = zeros((numbpopl, numbener, npixl, numbspec))
    for k in range(numbsamp):
        for l in indxpopl:
            for i in indxener:
                for h in range(numbspec):
                    indxpnts = where((binsspec[i, h] < listspec[l][k, i, :]) & (listspec[l][k, i, :] < binsspec[i, h+1]))[0]
                    hpixl = retr_pixl(listbgal[l][k, indxpnts], listlgal[l][k, indxpnts])
                    pntsprob[l, i, hpixl, h] += 1.
    
    
        
    if verbtype > 0:
        print 'Performing Gelman-Rubin convergence test...'
        tim0 = time.time()

    gmrbstat = zeros(ngpixl)
    for n in range(ngpixl):
        gmrbstat[n] = gmrb_test(listmodlcnts[:, :, n])


            
    pathprobcatl = os.environ["PNTS_TRAN_DATA_PATH"] + '/probcatl_' + datetimestrg + '_' + rtag + '.fits'  
    
    head = pf.Header()
    head['numbener'] = (numbener, 'Number of energy bins')
    head['numbevtt'] = (numbevtt, 'Number of PSF class bins')
    head['numbpopl'] = (numbpopl, 'Number of PS population')
    head['numbpsfipara'] = numbpsfipara
    head['nformpara'] = nformpara
    
    head['numbsamp'] = numbsamp
    head['numbburn'] = numbburn
    head['numbswep'] = numbswep
    head['factthin'] = factthin
    head['numbpopl'] = numbpopl
    head['numbproc'] = numbproc
    
    head['maxmgang'] = maxmgang
    head['lgalcntr'] = lgalcntr
    head['bgalcntr'] = bgalcntr
    head['numbspec'] = numbspec
    head['nsideheal'] = nsideheal
    head['nsidecart'] = nsidecart
    
    head['minmlgal'] = minmlgal
    head['maxmlgal'] = maxmlgal
    head['minmbgal'] = minmbgal
    head['maxmbgal'] = maxmbgal
    
    head['datatype'] = datatype
    head['regitype'] = regitype
    head['modlpsfntype'] = modlpsfntype
    if datatype == 'mock':
        head['mockpsfntype'] = mockpsfntype
    head['exprtype'] = exprtype
    head['pixltype'] = pixltype
    
    head['colrprio'] = colrprio
    head['trueinfo'] = trueinfo
    head['margsize'] = margsize
    head['datetimestrg'] = datetimestrg
    
    head['levi'] = levi
    head['info'] = info
    
    listhdun = []
    listhdun.append(pf.PrimaryHDU(header=head))
    for l in indxpopl:
        listhdun.append(pf.ImageHDU(listlgal[l]))
        listhdun[-1].header['EXTNAME'] = 'lgalpopl%d' % l
        listhdun.append(pf.ImageHDU(listbgal[l]))
        listhdun[-1].header['EXTNAME'] = 'bgalpopl%d' % l
        listhdun.append(pf.ImageHDU(listspec[l]))
        listhdun[-1].header['EXTNAME'] = 'specpopl%d' % l
        # temp
        if colrprio:
            listhdun.append(pf.ImageHDU(listsind[l]))
            listhdun[-1].header['EXTNAME'] = 'sindpopl%d' % l

    
    listhdun.append(pf.ImageHDU(listnumbpnts))
    listhdun[-1].header['EXTNAME'] = 'numbpnts'

    listhdun.append(pf.ImageHDU(listfdfnnorm))
    listhdun[-1].header['EXTNAME'] = 'fdfnnorm'
    
    listhdun.append(pf.ImageHDU(listfdfnslop))
    listhdun[-1].header['EXTNAME'] = 'fdfnslop'
    
    listhdun.append(pf.ImageHDU(listpsfipara))
    listhdun[-1].header['EXTNAME'] = 'psfipara'
    
    listhdun.append(pf.ImageHDU(listnormback))
    listhdun[-1].header['EXTNAME'] = 'normback'
    
    listhdun.append(pf.ImageHDU(listspechist))
    listhdun[-1].header['EXTNAME'] = 'spechist'
    
    
    listhdun.append(pf.ImageHDU(listllik))
    listhdun[-1].header['EXTNAME'] = 'llik'
    listhdun.append(pf.ImageHDU(listlpri))
    listhdun[-1].header['EXTNAME'] = 'lpri'
    
    # convergence diagnostics
    listhdun.append(pf.ImageHDU(gmrbstat))
    listhdun[-1].header['EXTNAME'] = 'gmrbstat'
    listhdun.append(pf.ImageHDU(listmodlcnts))
    listhdun[-1].header['EXTNAME'] = 'modlcnts'
    
    
    listhdun.append(pf.ImageHDU(pntsprob))
    listhdun[-1].header['EXTNAME'] = 'pntsprob'
    
    
    # truth information
    if trueinfo:
        listhdun.append(pf.ImageHDU(truenumbpnts))
        listhdun[-1].header['EXTNAME'] = 'truenumbpnts'

        for l in indxpopl:
            listhdun.append(pf.ImageHDU(truelgal[l]))
            listhdun[-1].header['EXTNAME'] = 'truelgalpopl%d' % l

            listhdun.append(pf.ImageHDU(truebgal[l]))
            listhdun[-1].header['EXTNAME'] = 'truebgalpopl%d' % l

            listhdun.append(pf.ImageHDU(truespec[l]))
            listhdun[-1].header['EXTNAME'] = 'truespecpopl%d' % l

        listhdun.append(pf.ImageHDU(truefdfnnorm))
        listhdun[-1].header['EXTNAME'] = 'truefdfnnorm'

        listhdun.append(pf.ImageHDU(truefdfnslop))
        listhdun[-1].header['EXTNAME'] = 'truefdfnslop'

        listhdun.append(pf.ImageHDU(truenormback))
        listhdun[-1].header['EXTNAME'] = 'truenormback'

        listhdun.append(pf.ImageHDU(truepsfipara))
        listhdun[-1].header['EXTNAME'] = 'truepsfipara'

        
    # boundaries
    listhdun.append(pf.ImageHDU(minmspec))
    listhdun[-1].header['EXTNAME'] = 'minmspec'
    listhdun.append(pf.ImageHDU(maxmspec))
    listhdun[-1].header['EXTNAME'] = 'maxmspec'
    listhdun.append(pf.ImageHDU(binsspec))
    listhdun[-1].header['EXTNAME'] = 'binsspec'
    listhdun.append(pf.ImageHDU(meanspec))
    listhdun[-1].header['EXTNAME'] = 'meanspec'

    if colrprio:
        listhdun.append(pf.ImageHDU(minmsind))
        listhdun[-1].header['EXTNAME'] = 'minmsind'
        listhdun.append(pf.ImageHDU(maxmsind))
        listhdun[-1].header['EXTNAME'] = 'maxmsind'
        listhdun.append(pf.ImageHDU(binssind))
        listhdun[-1].header['EXTNAME'] = 'binssind'
        listhdun.append(pf.ImageHDU(meansind))
        listhdun[-1].header['EXTNAME'] = 'meansind'
    
    listhdun.append(pf.ImageHDU(binsener))
    listhdun[-1].header['EXTNAME'] = 'binsener'
    listhdun.append(pf.ImageHDU(meanener))
    listhdun[-1].header['EXTNAME'] = 'meanener'
    
    
    listhdun.append(pf.ImageHDU(jener))
    listhdun[-1].header['EXTNAME'] = 'jener'
    
    listhdun.append(pf.ImageHDU(jevtt))
    listhdun[-1].header['EXTNAME'] = 'jevtt'
    
    
    # utilities
    
    listhdun.append(pf.ImageHDU(listpntsfluxmean))
    listhdun[-1].header['EXTNAME'] = 'listpntsfluxmean'
    
    listhdun.append(pf.ImageHDU(probprop))
    listhdun[-1].header['EXTNAME'] = 'probprop'

    listhdun.append(pf.ImageHDU(listindxprop))
    listhdun[-1].header['EXTNAME'] = 'indxprop'
    
    listhdun.append(pf.ImageHDU(listchro))
    listhdun[-1].header['EXTNAME'] = 'chro'
    
    listhdun.append(pf.ImageHDU(listaccp))
    listhdun[-1].header['EXTNAME'] = 'accp'
    
    listhdun.append(pf.ImageHDU(listindxsampmodi))
    listhdun[-1].header['EXTNAME'] = 'sampmodi'
    
    listhdun.append(pf.ImageHDU(listauxipara))
    listhdun[-1].header['EXTNAME'] = 'auxipara'
    
    listhdun.append(pf.ImageHDU(listlaccfrac))
    listhdun[-1].header['EXTNAME'] = 'laccfrac'
    
    listhdun.append(pf.ImageHDU(listnumbpair))
    listhdun[-1].header['EXTNAME'] = 'numbpair'
    
    listhdun.append(pf.ImageHDU(listjcbnfact))
    listhdun[-1].header['EXTNAME'] = 'jcbnfact'
    
    listhdun.append(pf.ImageHDU(listcombfact))
    listhdun[-1].header['EXTNAME'] = 'combfact'
    
    pf.HDUList(listhdun).writeto(pathprobcatl, clobber=True)
    
    
    
    if makeplot:
        plot_post(pathprobcatl)

    timetotlreal = time.time() - timetotlreal
    timetotlproc = time.clock() - timetotlproc
     
    # temp
    #os.system(cmnd)
    
    if verbtype > 0:
        for k in range(numbproc):
            print 'Process %d has been completed in %d real seconds, %d CPU seconds.' % (k, timereal[k], timeproc[k])
        print 'PNTS_TRAN has run in %d real seconds, %d CPU seconds.' % (timetotlreal, sum(timeproc))
        print 'The ensemble of catalogs is at ' + pathprobcatl
        if makeplot:
            print 'The plots are in ' + plotpath
        
    return gridchan
    


# In[ ]:




# In[167]:

def plot_minmspecinfo(minmspecarry, listinfo, listlevi):
    
    
    figr, axis = plt.subplots(figsize=(14, 10))
    ax_ = axis.twinx()
    axis.plot(minmspecarry, listinfo, label='Relative entropy')
    axis.legend(bbox_to_anchor=[0.3, 1.08], loc=2)
    
    ax_.plot(minmspecarry, listlevi, label='Log-evidence', color='g')
    ax_.legend(bbox_to_anchor=[0.7, 1.08])

    axis.set_ylabel('$D_{KL}$ [nats]')
    ax_.set_ylabel(r'$\log P(D)$ [nats]')
    axis.set_xlabel('$f_{min}$ [1/cm$^2$/s/GeV]')
    axis.set_xscale('log')
    figr.savefig(os.environ["PNTS_TRAN_DATA_PATH"] + '/png/minmspecinfo.png')
    plt.close(figr)
    


# In[168]:

def retr_cnfg(               verbtype=1,               
              plotperd=50000, \
              
              makeplot=True, \
              
              diagsamp=False, \
              
              numbswep=1000000, \
              numbburn=None, \
              factthin=None, \
              
              regitype='ngal', \
              datatype='inpt', \
              randinit=True, \
              

              maxmgang=None, \
              
              minmspec=None, \
              maxmspec=None, \
              minmsind=None, \
              maxmsind=None, \
              
              minmfdfnnorm=None, \
              maxmfdfnnorm=None, \
              minmfdfnslop=None, \
              maxmfdfnslop=None, \

              
              psfntype='doubking', \
              
              colrprio=False, \
              
              numbpopl=1, \
              
              jevtt=arange(2, 4), \
              jener=arange(5), \
              
              maxmnumbpnts=array([200]), \

              initnumbpnts=None, \
              trueinfo=False, \
              pntscntr=False, \
              
              numbproc=None, \
              
              liketype='pois', \
              pixltype='heal', \
              exprtype='ferm', \
              
              lgalcntr=0., \
              bgalcntr=0., \
              

              
              margsize=None, \
              mocknumbpnts=None, \

              mockfdfnnorm=None, \
              mockfdfnslop=None, \

              maxmnormback=None, \
              minmnormback=None, \
              
              nsidecart=None, \
              nsideheal=None, \
              
              # temp
              maxmangleval=5., \
              
              spmrlbhl=2., \
            
              stdvlbhl=0.1, \
              stdvback=0.04, \
              stdvspec=0.15, \
              
              stdvfdfnnorm=0.05, \
              stdvfdfnslop=0.001, \
              stdvpsfipara=0.1, \
              
              fracrand=0.05, \
              
              mocknormback=None, \
              
              exprfluxstrg=None, \
              listbackfluxstrg=None, \
              expostrg=None, \
              
              probprop=None, \
              
             ):
    
    
    # experiment-specific defaults
    if exprtype == 'ferm':
        
        # prior boundaries
        if maxmgang == None:
            maxmgang = 20.
            
        if minmsind == None:
            minmsind = array([1.])
        if maxmsind == None:
            maxmsind = array([3.])
            
            
        if minmfdfnnorm == None:
            minmfdfnnorm = 1e0
        if maxmfdfnnorm == None:
            maxmfdfnnorm = 1e2
        if minmfdfnslop == None:
            minmfdfnslop = 1.5
        if maxmfdfnslop == None:
            maxmfdfnslop = 2.5
            
        if margsize == None:
            margsize = 1.
        
    
    cnfg = dict()

    # verbosity level
    ## 0 - no output
    ## 1 - progress
    ## 2 - sampler diagnostics
    cnfg['verbtype'] = verbtype
    
    # plot settings
    ## MCMC time period over which a frame is produced
    cnfg['plotperd'] = plotperd
    ## flag to control generation of plots
    cnfg['makeplot'] = makeplot

    # flag to diagnose the sampler
    cnfg['diagsamp'] = diagsamp
    
    # MCMC setup
    ## number of sweeps, i.e., number of samples before thinning and including burn-in
    cnfg['numbswep'] = numbswep
    ## number of burn-in samples
    cnfg['numbburn'] = numbburn
    ## number of processes
    cnfg['numbproc'] = numbproc
    ## the factor by which to thin the chain
    cnfg['factthin'] = factthin
    
    # region type
    #- ngal - NGPR (North Galactic Polar Region)
    #- igal - IG (inner Galaxy)
    cnfg['regitype'] = regitype

    # data type
    #- mock - mock data
    #- inpt - input data
    cnfg['datatype'] = datatype
    
    # likelihood function type
    cnfg['liketype'] = liketype
    
    # experiment type
    cnfg['exprtype'] = exprtype
    
    # pixelization type
    cnfg['pixltype'] = pixltype
    
    # PSF model type
    cnfg['modlpsfntype'] = modlpsfntype
    
    if datatype == 'mock':
        cnfg['mockpsfntype'] = mockpsfntype
        
    # color priors
    cnfg['colrprio'] = colrprio
    
    # input data
    cnfg['exprfluxstrg'] = exprfluxstrg
    cnfg['listbackfluxstrg'] = listbackfluxstrg
    cnfg['expostrg'] = expostrg
    
    # flag to use truth information
    cnfg['trueinfo'] = trueinfo
    
    # initial state setup
    ## number of point sources
    cnfg['initnumbpnts'] = initnumbpnts
    ## flag to draw the initial state from the prior
    cnfg['randinit'] = randinit

    # energy bins to be included
    cnfg['jener'] = jener
    
    # PSF bins to be included
    cnfg['jevtt'] = jevtt
    
    # number of Point Source (PS) populations
    cnfg['numbpopl'] = numbpopl
    
    # maximum angle from the PSs to evaluate the likelihood
    cnfg['maxmangleval'] = maxmangleval
    
    # parameter limits
    ## flux distribution function normalization
    cnfg['minmfdfnnorm'] = minmfdfnnorm
    cnfg['maxmfdfnnorm'] = maxmfdfnnorm
    ## flux distribution function power law index
    cnfg['minmfdfnslop'] = minmfdfnslop
    cnfg['maxmfdfnslop'] = maxmfdfnslop
    ## flux
    cnfg['minmsind'] = minmsind
    cnfg['maxmsind'] = maxmsind
    ## spectral power-law index
    cnfg['minmspec'] = minmspec
    cnfg['maxmspec'] = maxmspec
    ## background normalizations
    cnfg['minmnormback'] = minmnormback
    cnfg['maxmnormback'] = maxmnormback

    
    # model indicator limits
    cnfg['maxmnumbpnts'] = maxmnumbpnts
    
    # Region of interest
    ## image center
    cnfg['lgalcntr'] = lgalcntr
    cnfg['bgalcntr'] = bgalcntr
    ## half of the image size
    cnfg['maxmgang'] = maxmgang
    ## image margin size
    cnfg['margsize'] = margsize

    # proposals
    ## proposal scales
    cnfg['stdvfdfnnorm'] = stdvfdfnnorm
    cnfg['stdvfdfnslop'] = stdvfdfnslop
    cnfg['stdvpsfipara'] = stdvpsfipara
    cnfg['stdvback'] = stdvback
    cnfg['stdvlbhl'] = stdvlbhl
    cnfg['stdvspec'] = stdvspec

    ## fraction of heavy-tailed proposals
    cnfg['fracrand'] = fracrand
    
    ## maximum angle over which splits and merges are proposed
    cnfg['spmrlbhl'] = spmrlbhl
    
    # mock data setup
    ## mock parameters
    cnfg['mocknumbpnts'] = mocknumbpnts
    cnfg['mockfdfnnorm'] = mockfdfnnorm
    cnfg['mockfdfnslop'] = mockfdfnslop
    cnfg['mocknormback'] = mocknormback
    ## flag to position mock point sources at the image center
    cnfg['pntscntr'] = pntscntr
    ## mock image resolution
    cnfg['nsidecart'] = nsidecart
    cnfg['nsideheal'] = nsideheal

    # proposal frequencies
    cnfg['probprop'] = probprop

    return cnfg


# In[169]:

def cnfg_ferm_psfn_expr(modlpsfntype):
     

    cnfg = retr_cnfg(                      numbswep=100000,                      factthin=1,                      plotperd=20000,                      trueinfo=True,                      randinit=False,                      datatype='inpt',                      modlpsfntype=modlpsfntype,                      maxmgang=10.,                      minmspec=array([3e-10, 3e-11, 3e-12]),                      maxmspec=array([1e-6, 1e-7, 1e-8]),                      regitype='ngal',                      exprfluxstrg='fermflux_ngal.fits',                      listbackfluxstrg=['fermisotflux.fits', 'fermfdfmflux_ngal.fits'],                      expostrg='fermexpo_ngal.fits',                      maxmnormback=array([5., 5.]),                      minmnormback=array([0.2, 0.2]),                      stdvback=0.05,                      probprop=array([0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.]),                     )
                
    init(cnfg)
    
    
        


# In[170]:

def cnfg_ferm_info():
    
    nruns = 2
    listlevi = zeros(nruns)
    listinfo = zeros(nruns)
    minmspec = logspace(-12., -7., nruns)

    for k in range(nruns):
        
        cnfg = retr_cnfg(                          modlpsfntype='gausking',                          numbswep=50000,                          plotperd=50000,                          trueinfo=True,                          randinit=False,                          maxmgang=10.,                          maxmnumbpnts=array([3000]),                          colrprio=True,                          jener=arange(1),                          jevtt=arange(3, 4),                          minmspec=array([minmspec[k]]),                          maxmspec=array([3e-7]),                          regitype='ngal',                          maxmnormback=array([5., 5.]),                          minmnormback=array([0.2, 0.2]),                          listbackfluxstrg=['fermisotflux.fits', 'fermfdfmflux_ngal.fits'],                          expostrg='fermexpo_ngal.fits',                          stdvback=0.1,                          datatype='mock',                          mocknumbpnts=array([100]),                          nsideheal=256,                          makeplot=False,                          mockpsfntype='gausking',                          mocknormback=ones((2, 3)),                         )
        
        gridchan = init(cnfg)
        numbproc = len(gridchan)
        for l in range(numbproc):
            listchan = gridchan[l]
            listlevi[k] = listchan[14]
            listinfo[k] = listchan[15]

    plot_minmspecinfo(minmspec, listinfo, listlevi)


# In[171]:

def cnfg_ferm_expr_igal(exprfluxstrg, expostrg):
      
    cnfg = retr_cnfg(                      modlpsfntype='gausking',                      numbswep=3000000,                      numbburn=1500000,                      verbtype=1,                      makeplot=True,                      plotperd=50000,                      initnumbpnts=array([100]),                      maxmnumbpnts=array([600]),                      trueinfo=True,                      randinit=False,                      maxmgang=20.,                      colrprio=False,                      #jener=arange(1), \
                     #jevtt=arange(3, 4), \
                     #minmspec=array([1e-8]), \
                     #maxmspec=array([3e-6]), \
                     minmspec=array([1e-8, 1e-9, 1e-10, 1e-11, 1e-12]), \
                     maxmspec=array([3e-6, 3e-7, 3e-8, 3e-9, 3e-10]), \
                     regitype='igal', \
                     maxmnormback=array([2., 2.]), \
                     minmnormback=array([0.5, 0.5]), \
                     listbackfluxstrg=['fermisotflux.fits', 'fermfdfmflux_ngal.fits'], \
                     expostrg=expostrg, \
                     stdvback=0.1, \
                     datatype='inpt', \
                     exprfluxstrg=exprfluxstrg, \
                    )
        
    init(cnfg)


# In[172]:

def cnfg_ferm_mock_igal():
     
    cnfg = retr_cnfg(                      modlpsfntype='singking',                      numbswep=1000000,                      plotperd=50000,                      nsideheal=256,                      maxmgang=10.,                      minmspec=array([1e-9, 1e-10, 1e-11]),                      maxmspec=array([1e-6, 1e-7, 1e-8]),                      maxmnormback=array([5., 5.]),                      minmnormback=array([0.2, 0.2]),                      mocknormback=ones((2, 3)),                      regitype='igal',                      listbackfluxstrg=['fermisotflux.fits', 'fermfdfm.fits'],                      expostrg='fermexpo_igal.fits',                      stdvback=0.05,                      trueinfo=True,                      randinit=False,                      mockpsfntype='gausking',                      datatype='mock'                     )

    init(cnfg)
    


# In[173]:

def cnfg_ferm_expr_ngal(exprfluxstrg, expostrg):
     
    colrprio = False
    
    if colrprio:
        minmspec = array([1e-11])
        maxmspec = array([1e-7])
    else:
        minmspec = array([3e-9, 3e-10, 3e-11, 3e-12, 3e-13])
        maxmspec = array([1e-5, 1e-6, 1e-7, 1e-8, 1e-9])
        
    cnfg = retr_cnfg(                      modlpsfntype='gausking',                      numbswep=200000,                      numbburn=50000,                      verbtype=1,                      makeplot=True,                      plotperd=50000,                      initnumbpnts=array([100]),                      maxmnumbpnts=array([200]),                      trueinfo=True,                      randinit=False,                      maxmgang=20.,                      colrprio=colrprio,                      jener=arange(5),                      jevtt=arange(2, 4),                      minmspec=minmspec,                      maxmspec=maxmspec,                      regitype='ngal',                      maxmnormback=array([2., 2.]),                      minmnormback=array([0.5, 0.5]),                      listbackfluxstrg=['fermisotflux.fits', 'fermfdfmflux_ngal.fits'],                      expostrg=expostrg,                      stdvback=0.1,                      datatype='inpt',                      exprfluxstrg=exprfluxstrg,                     )
                
    init(cnfg)


# In[174]:

def cnfg_ferm_mock_ngal():
     
    colrprio = False
    
    if colrprio:
        minmspec = array([3e-11])
        maxmspec = array([1e-7])
        mockfdfnslop = array([[1.8]])
    else:
        minmspec = array([3e-9, 3e-10, 3e-11, 3e-12, 3e-13])
        maxmspec = array([1e-5, 1e-6, 1e-7, 1e-8, 1e-9])
        mockfdfnslop = array([[1.8, 1.8, 1.8, 1.8, 1.8]])
      
    
    cnfg = retr_cnfg(                      modlpsfntype='gausking',                      numbswep=200000,                      plotperd=50000,                      trueinfo=True,                      randinit=False,                      maxmgang=20.,                      colrprio=colrprio,                      verbtype=1,                      jevtt=arange(3, 4),                      jener=arange(5),                      maxmnumbpnts=array([200]),                      mocknumbpnts=array([100]),                      probprop=array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], dtype=float),                      minmspec=minmspec,                      maxmspec=maxmspec,                      regitype='ngal',                      maxmnormback=array([2., 2.]),                      minmnormback=array([0.5, 0.5]),                      listbackfluxstrg=['fermisotflux.fits', 'fermfdfmflux_ngal.fits'],                      expostrg='fermexpo_ngal_comp.fits',                      stdvback=0.1,                      datatype='mock',                      nsideheal=256,                      mockfdfnslop=mockfdfnslop,                      mockfdfnnorm=array([10.]),                      mocknormback=ones((2, 5)),                      mockpsfntype='gausking',                     )

    init(cnfg)
    


# In[175]:

def cnfg_sdss_mock():

    cnfg = retr_cnfg(psfntype='doubgaus',                      trueinfo=False,                      numbswep=100000,                      plotperd=20000,                      verbtype=1,                      minmspec=ones(3) * 1e3,                      maxmspec=ones(3) * 1e5,                      initnumbpnts=array([100]),                      exprtype='sdss',                      datatype='mock',                      pixltype='cart',                      regitype='mes5',                      stdvlbhl=2./3600.,                      lgalcntr=202.,                      bgalcntr=2.,                      mocknormback=ones((1, 3)),                      spmrlbhl=5./3600.,                      maxmnormback=array([1e3]),                      minmnormback=array([1e2]),                      maxmgang=30./3600.,                      nsidecart=100,                      margsize=2./3600.,                      maxmangleval=10./3600.,                      listbackfluxstrg=['sdssisotflux.fits'],                      expostrg='sdssexpo.fits',                      stdvback=0.01,                      jevtt=arange(1),                      jener=arange(1)                     )

    init(cnfg)
    


# In[176]:

def cnfg_sdss_expr():

    cnfg = retr_cnfg(psfntype='doubgaus',                      trueinfo=False,                      numbswep=1000000,                      plotperd=20000,                      verbtype=1,                      minmspec=ones(3) * 1e3,                      maxmspec=ones(3) * 1e5,                      initnumbpnts=array([10]),                      maxmnumbpnts=20,                      exprtype='sdss',                      datatype='inpt',                      pixltype='cart',                      regitype='mes5',                      stdvlbhl=2./3600.,                      lgalcntr=202.,                      bgalcntr=2.,                      spmrlbhl=0.5/3600.,                      stdvspec=0.05,                      maxmnormback=array([1e3]),                      minmnormback=array([1e2]),                      margsize=2./3600.,                      maxmgang=30./3600.,                      maxmangleval=10./3600.,                      exprfluxstrg='sdssflux.fits',                      listbackfluxstrg=['sdssisotflux.fits'],                      expostrg='sdssexpo.fits',                      stdvback=1e-4,                      jevtt=arange(1),                      jener=arange(1)                     )

    init(cnfg)
    


# In[177]:

if __name__ == '__main__':
    
    pass

    #cnfg_ferm_info()
    
    #cnfg_ferm_psfn_mock('gausking')
    #cnfg_ferm_psfn_mock('doubking')

    #cnfg_ferm_psfn_expr('gausking')
    #cnfg_ferm_psfn_expr('doubking')
    
    #cnfg_ferm_expr_igal('fermflux_igal_comp_time0.fits', 'fermexpo_igal_comp_time0.fits')
    #cnfg_ferm_mock_igal()
    
    #cnfg_ferm_expr_ngal('fermflux_comp_ngal.fits', 'fermexpo_comp_ngal.fits')
    #cnfg_ferm_expr_ngal('fermflux_ngal_comp_time0.fits', 'fermexpo_ngal_comp_time0.fits')
    #cnfg_ferm_expr_ngal('fermflux_ngal_comp_time1.fits', 'fermexpo_ngal_comp_time1.fits')
    #cnfg_ferm_expr_ngal('fermflux_ngal_comp_time2.fits', 'fermexpo_ngal_comp_time2.fits')
    #cnfg_ferm_expr_ngal('fermflux_ngal_comp_time3.fits', 'fermexpo_ngal_comp_time3.fits')
    #cnfg_ferm_expr_ngal('fermflux_ngal_full.fits', 'fermexpo_ngal_full.fits')
    cnfg_ferm_mock_ngal()
    
    #cnfg_sdss_mock()
    #cnfg_sdss_expr()


# In[ ]:



