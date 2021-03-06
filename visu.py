# common imports
from __init__ import *

# internal functions
from util import *

def plot_samp(gdat, gdatmodi=None):
   
    if gdatmodi != None:
        # do necessary preprocessing for frame plots
        if gdat.numbtrap > 0:
            for l in gdat.indxpopl:
                gdatmodi.indxmodlpntscomp[l] = retr_indxpntscomp(gdat, gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l]], gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l]])

        retr_thismodlflux(gdat, gdatmodi)

        if gdat.pixltype != 'unbd':
            gdatmodi.thismodlcnts = gdatmodi.thismodlflux * gdat.expo * gdat.apix
            if gdat.enerbins:
                gdatmodi.thismodlcnts *= gdat.diffener[:, None, None]
            gdatmodi.thisresicnts = gdat.datacnts - gdatmodi.thismodlcnts
   
        if gdat.pntstype == 'lght':
            
            gdatmodi.thispntsfluxmean = sum(sum(gdatmodi.thispntsflux * gdat.expo, 2), 1) / sum(sum(gdat.expo, 2), 1)

            # PSF radial profile
            if gdat.varioaxi:
                for p in gdat.indxoaxi:
                    gdatmodi.thispsfn[:, :, :, p] = gdatmodi.thispsfnintp[p](gdat.binsangl)
            else:
                gdatmodi.thispsfn = gdatmodi.thispsfnintp(gdat.binsangl)

            # PSF FWHM
            gdatmodi.thisfwhm = 2. * retr_psfnwdth(gdat, gdatmodi.thispsfn, 0.5)
   
        if gdat.pixltype != 'unbd' and gdat.pntstype == 'lght':
            # number of background counts per PSF
            gdatmodi.thiscntsbackfwhm = retr_cntsbackfwhm(gdat, gdatmodi.thissampvarb[gdat.indxfixpbacp], gdatmodi.thisfwhm)
        
            # number of counts and standard deviation of each PS
            gdatmodi.thiscnts = []
            gdatmodi.thissigm = []
            for l in gdat.indxpopl:
                # temp -- zero exposure pixels will give zero counts
                indxpixltemp = retr_indxpixl(gdat, gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l]], gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l]])
                cntstemp = gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l]][:, :, None] * gdat.expofull[:, indxpixltemp, :]
                if gdat.enerbins:
                    cntstemp *= gdat.diffener[:, None, None]
                gdatmodi.thiscnts.append(cntstemp)
                if gdat.varioaxi:
                    sigmtemp = retr_sigm(gdat, cntstemp, gdatmodi.thiscntsbackfwhm, lgal=gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l]], \
                                                                                    bgal=gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l]])
                else:
                    sigmtemp = retr_sigm(gdat, cntstemp, gdatmodi.thiscntsbackfwhm)
                gdatmodi.thissigm.append(sigmtemp)
            
            # standard deviation axis
            gdatmodi.binssigm = retr_sigm(gdat, gdat.binscnts, gdatmodi.thiscntsbackfwhm)
    
        # temp -- list may not be the ultimate solution to copy gdatmodi.thisindxpntsfull
        if gdat.calcerrr and gdat.numbtrap > 0:
            temppntsflux, temppntscnts, tempmodlflux, tempmodlcnts = retr_maps(gdat, list(gdatmodi.thisindxpntsfull), copy(gdatmodi.thissampvarb), evalcirc=False)
            gdatmodi.thiserrrcnts = gdatmodi.thispntscnts - temppntscnts
            gdatmodi.thiserrr = zeros_like(gdatmodi.thiserrrcnts)
            indxcubegood = where(temppntscnts > 1e-10)
            gdatmodi.thiserrr[indxcubegood] = 100. * gdatmodi.thiserrrcnts[indxcubegood] / temppntscnts[indxcubegood]
            if False and amax(fabs(gdatmodi.thiserrr)) > 0.1:
                raise Exception('Approximation error in calculating the PS flux map is above the tolerance level.')
    

        if gdat.numbtrap > 0 and gdat.trueinfo:
            gdatmodi.trueindxpntsassc = []
            gdatmodi.thisspecassc = []
            for l in gdat.indxpopl:
                indxmodl, trueindxpntsassc = corr_catl(gdat, l, gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l]], gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l]], \
                                                                                                                            gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l]])
                gdatmodi.trueindxpntsassc.append(trueindxpntsassc)
                gdatmodi.thisspecassc.append(zeros((gdat.numbener, gdat.truefixp[gdat.indxfixpnumbpnts[l]])))
                temp = where(indxmodl >= 0)[0]
                gdatmodi.thisspecassc[l][:, temp] = gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l]][:, indxmodl[temp]]
                gdatmodi.thisspecassc[l][:, gdatmodi.trueindxpntsassc[l].miss] = 0.

        if gdat.pntstype == 'lens':
            gdatmodi.thisconv = retr_conv(gdat, gdatmodi.thisdefl) 
            gdatmodi.thisconvpsec = retr_psec(gdat, gdatmodi.thisconv)
            gdatmodi.thisconvpsecodim = retr_psecodim(gdat, gdatmodi.thisconvpsec) 

    # plots
    ## frame-only
    if gdatmodi != None:
        ## brightest PS
        if gdat.pntstype == 'lght':
            if gdatmodi == None or sum(gdatmodi.thissampvarb[gdat.indxfixpnumbpnts]) != 0:
                plot_brgt(gdat, gdatmodi)

    ## PSF radial profile
    if gdat.pntstype == 'lght':
        plot_psfn(gdat, gdatmodi)

        if gdat.varioaxi or gdat.truevarioaxi:
            for i in gdat.indxener:
                for m in gdat.indxevtt:
                    plot_factoaxi(gdat, i, m, gdatmodi)
    
        ## PSF FWHM
        if False:
            plot_fwhm(gdat, gdatmodi)
    
    # number of background counts per PSF
    if False:
        for i in gdat.indxener:
            path = gdat.pathplot + 'cntsbackfwhmflux%d_%09d.pdf' % (i, gdatmodi.cntrswep)
            tdpy.util.plot_maps(path, sum(gdatmodi.thiscntsbackfwhm, 2)[i, :], pixltype=gdat.pixltype, indxpixlrofi=gdat.indxpixlrofi, numbpixl=gdat.numbpixlfull, \
                                                                                                minmlgal=gdat.anglfact*gdat.minmlgal, maxmlgal=gdat.anglfact*gdat.maxmlgal, \
                                                                                                minmbgal=gdat.anglfact*gdat.minmbgal, maxmbgal=gdat.anglfact*gdat.maxmbgal)

    if gdat.numbtrap > 0:
        for l in gdat.indxpopl:
            if gdat.trueinfo:
                plot_scatspec(gdat, l, gdatmodi)
                plot_scatspec(gdat, l, gdatmodi, plotdiff=True)
    
            plot_histspec(gdat, l, gdatmodi)
            if gdat.pntstype == 'lght' and gdat.numbener > 1:
                plot_histsind(gdat, l, gdatmodi)
                plot_fluxsind(gdat, l, gdatmodi, 'hist')
                if gdatmodi != None:
                    plot_fluxsind(gdat, l, gdatmodi, 'scat')
            # temp -- restrict compfrac and other plots to indxmodlpntscomp
            if gdat.correxpo and gdat.pntstype == 'lght':
                plot_histcnts(gdat, l, gdatmodi)
            if gdat.pntstype == 'lght':
                plot_compfrac(gdat, gdatmodi)
    
    for i in gdat.indxener:
        for m in gdat.indxevttplot:
            plot_scatpixl(gdat, gdatmodi)
    
    if gdat.pntstype == 'lens':
        plot_genemaps(gdat, 'conv', gdatmodi)
        plot_gene(gdat, gdatmodi, 'convpsecodim', 'wvecodim', scal='logt', lablxaxi='$k$ [1/kpc]', lablyaxi='$P(k)$')

    for l in gdat.indxpopl:
        for i in gdat.indxener:
            for m in gdat.indxevttplot:
                if gdatmodi != None:
                    plot_datacnts(gdat, l, gdatmodi, i, m)
                
                if gdat.pntstype == 'lens':
                    
                    plot_defl(gdat, gdatmodi)

                    if gdatmodi != None:
                        

                        if gdat.inclpnts:
                            numbpntsplot = min(3, gdatmodi.thissampvarb[gdat.indxfixpnumbpnts[l]].astype(int))
                            indxpntssortbrgt = argsort(gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l][gdat.indxenerfluxdist[0], :]])[::-1]
                            lgal = gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l][indxpntssortbrgt]][:numbpntsplot]
                            bgal = gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l][indxpntssortbrgt]][:numbpntsplot]
                            bein = gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l][gdat.indxenerfluxdist[0], indxpntssortbrgt]][:numbpntsplot]
                        else:
                            numbpntsplot = 0
                        numbplot = numbpntsplot + 1
                        for k in range(numbplot):
                            if k == 0:
                                lensobjt = franlens.LensModel(gdat.truelenstype, gdatmodi.thissampvarb[gdat.indxfixplgalhost], \
                                                                                 gdatmodi.thissampvarb[gdat.indxfixpbgalhost], \
                                                                                 gdatmodi.thissampvarb[gdat.indxfixpellphost], \
                                                                                 gdatmodi.thissampvarb[gdat.indxfixpanglhost], \
                                                                                 gdatmodi.thissampvarb[gdat.indxfixpsherhost], \
                                                                                 gdatmodi.thissampvarb[gdat.indxfixpsanghost], \
                                                                                 gdatmodi.thissampvarb[gdat.indxfixpbeinhost])
                            else:
                                lensobjt = franlens.LensModel(gdat.truelenstype, lgal[k-1], bgal[k-1], 0., 0., 0., 0., bein[k-1])
                            defl = lensobjt.deflection(gdat.lgalgridcart, gdat.bgalgridcart)
                            plot_defl(gdat, gdatmodi=gdatmodi, defl=defl, indxdefl=k)

                if gdat.pixltype == 'unbd':
                    plot_catlfram(gdat, gdatmodi, l, i, m)
                else:
                    plot_modlcnts(gdat, l, gdatmodi, i, m)
                    plot_resicnts(gdat, l, gdatmodi, i, m)
                if gdat.calcerrr and gdat.numbtrap > 0:
                    plot_errrcnts(gdat, gdatmodi, i, m)
  
            # temp
            #for m in gdat.indxevtt:
            #    plot_datacnts(gdat, gdatmodi, i, m)
            #    plot_catl(gdat, gdatmodi, i, m, thiscnts)
            #    plot_modlcnts(gdat, gdatmodi, i, m)
            #    plot_resicnts(gdat, gdatmodi, i, m)
    
    # temp
    #if gdat.numbener > 1:
    #    plot_datacnts(gdat, l, gdatmodi, None, None)
        

def plot_post(gdat=None, pathpcat=None, verbtype=1, makeanim=False, writ=True):
    
    if writ:
        gdat = tdpy.util.gdatstrt()
        gdat.verbtype = verbtype
        gdat.makeanim = makeanim

        if gdat.verbtype > 0:
            print 'Reading %s...' % pathpcat

        # read PCAT output file
        shel = shelve.open(pathpcat)
        for keyy in shel:
            if keyy == 'gdat':
                gdat = shel[keyy]
        shel.close()
    
    if gdat.verbtype > 0:
        print 'Producing postprocessing plots...'

    timetotlinit = gdat.functime()
    
    gdat.strgbest = 'ML'
    
    # Gelman-Rubin test
    # temp
    if False and gdat.numbproc > 1:
        if isfinite(gdat.gmrbstat).all():
            figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
            minm = min(amin(gdat.gmrbstat), amin(gdat.gmrbfixp))
            maxm = max(amax(gdat.gmrbstat), amax(gdat.gmrbfixp))
            bins = linspace(minm, maxm, 40)
            axis.hist(gdat.gmrbstat.flatten(), bins=bins, label='Data proj.')
            axis.hist(gdat.gmrbfixp, bins=bins, label='Fixed dim.')
            axis.set_xlabel('PSRF')
            axis.set_ylabel('$N_{stat}$')
            plt.tight_layout()
            plt.savefig(gdat.pathplot + 'diag/gmrbhist.pdf')
            plt.close(figr)
            
            for i in gdat.indxener:
                for m in gdat.indxevtt:
                    maps = zeros(gdat.numbpixl)
                    maps[gdat.indxpixlsave] = gdat.gmrbstat[i, :, m]
                    path = gdat.pathdiag + 'gmrbmaps_%d%d.pdf' % (i, m)
                    tdpy.util.plot_maps(path, maps, indxpixlrofi=gdat.indxpixlrofi, numbpixl=gdat.numbpixlfull, pixltype=gdat.pixltype, \
                                                                                            minmlgal=gdat.anglfact*gdat.minmlgal, maxmlgal=gdat.anglfact*gdat.maxmlgal, \
                                                                                            minmbgal=gdat.anglfact*gdat.minmbgal, maxmbgal=gdat.anglfact*gdat.maxmbgal)
        else:
            print 'Inappropriate Gelman-Rubin test statistics encountered.'

    # plot autocorrelation
    tdpy.mcmc.plot_atcr(gdat.pathdiag, gdat.atcr, gdat.timeatcr)
    
    # plot proposal efficiency
    if gdat.verbtype > 0:
        print 'Making proposal efficiency plots...'
    
    numbtimemcmc = 20
    binstimemcmc = linspace(0., gdat.numbswep, numbtimemcmc)
    numbtick = 2
    
    sizefigryaxi = max(gdat.numbprop * gdat.plotsize / 4., gdat.plotsize / 2.)
    figr, axgr = plt.subplots(gdat.numbprop, 1, figsize=(gdat.plotsize, sizefigryaxi), sharex='all')
    if gdat.numbprop == 1:
        axgr = [axgr]
    for n, axis in enumerate(axgr):
        histtotl = axis.hist(gdat.listindxsamptotlprop[n], bins=binstimemcmc)[0]
        histaccp = axis.hist(gdat.listindxsamptotlpropaccp[n], bins=binstimemcmc)[0]
        axis.set_ylabel('%s' % gdat.strgprop[n])
        if n == gdat.numbprop - 1:
            axis.set_xlabel('$i_{samp}$')
        # define the y-axis
        maxm = amax(histtotl)
        axis.set_ylim([0., maxm])
        try:
            axis.set_title('%.3g%%' % int(sum(histaccp) / sum(histtotl) * 100.))
        except:
            pass
        listtick = linspace(maxm / 2., maxm, numbtick)
        listlabltick = ['%.3g' % tick for tick in listtick]
        axis.set_yticks(listtick)
        axis.set_yticklabels(listlabltick)
    plt.tight_layout()
    plt.savefig(gdat.pathdiag + 'accpratiprop.pdf')
    plt.close(figr)
  
    # histogram of proposal types
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    binsprop = linspace(-0.5, gdat.numbprop - 0.5, gdat.numbprop + 1)
    axis.hist(gdat.listindxprop, bins=binsprop)[0]
    axis.set_ylabel('$N_{samp}$')
    axis.set_xlabel('$i_{prop}$')
    axis.set_xticks(gdat.indxprop)
    plt.tight_layout()
    plt.savefig(gdat.pathdiag + 'histindxprop.pdf')
    plt.close(figr)
   
    # plot split and merge diagnostics
    if gdat.numbtrap > 0 and gdat.probtran > 0. and gdat.probbrde < 1.:
        indxsampsplttotl = where(gdat.listindxprop == gdat.indxpropsplt)[0]
        indxsampsplt = intersect1d(where(gdat.listindxprop == gdat.indxpropsplt)[0], where(gdat.listboolreje == False)[0])
        indxsampmergtotl = where(gdat.listindxprop == gdat.indxpropmerg)[0]
        indxsampmerg = intersect1d(where(gdat.listindxprop == gdat.indxpropmerg)[0], where(gdat.listboolreje == False)[0])
        indxsampspmr = union1d(indxsampsplt, indxsampmerg)
        indxsampspmrtotl = union1d(indxsampsplttotl, indxsampmergtotl)
        indxsampreje = where(gdat.listboolreje == False)
        if indxsampspmrtotl.size > 0:
    
            ## create plot subfolder
            os.system('mkdir -p %s' % gdat.pathplot + 'spmr')
    
            ## labels and names
            listlabl = ['$u_f$', '$u_r$', r'$u_\phi$', '$u_s$', '$N_{pair}$', \
                                            r'$\alpha_c\alpha_j$', r'$\alpha_P\alpha_c\alpha_j$', r'$\alpha_c$', r'$\alpha_j$', r'$\alpha_L$', r'$\alpha_P$']
            listname = ['fracauxi', 'radiauxi', 'anglauxi', 'sindauxi', 'numbpair', 'laccfact', 'laccfacttotl', 'combfact', 'jcbnfct']
            
            ## variables
            listvarb = [gdat.listauxipara[:, 0], gdat.anglfact * gdat.listauxipara[:, 1], gdat.listauxipara[:, 2], gdat.listauxipara[:, 3], gdat.listnumbpair, \
                                             exp(gdat.listlaccfact), exp(gdat.listlaccfact + gdat.listdeltlpri), gdat.listcombfact, \
                                             gdat.listjcbnfact]
           
            print 'gdat.listauxipara'
            print gdat.listauxipara
            print 'gdat.listnumbpair'
            print gdat.listnumbpair
            print 'gdat.listlaccfact'
            print gdat.listlaccfact
            print 'gdat.listdeltlpri'
            print gdat.listdeltlpri
            print 'gdat.listcombfact'
            print gdat.listcombfact
            print
    
            # rescale the Jacobian and the prior fraction to make them dimensionless
            listvarb[5][indxsampsplttotl] /= gdat.minmflux
            listvarb[5][indxsampmergtotl] *= gdat.minmflux
            listvarb[8][indxsampsplttotl] /= gdat.minmflux
            listvarb[8][indxsampmergtotl] *= gdat.minmflux
            listvarb[10][indxsampsplttotl] *= gdat.minmflux
            listvarb[10][indxsampmergtotl] /= gdat.minmflux
    
            for k in range(len(listlabl)):
                figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
                maxm = amax(listvarb[k][indxsampspmrtotl])
                
                if k <= 4:
                    indxsampspmrtemp = indxsampspmrtotl
                    indxsampsplttemp = indxsampsplttotl
                else:
                    indxsampspmrtemp = indxsampspmr
                    indxsampsplttemp = indxsampsplt
                
                if k >= 5:
                    axis.set_xscale('log')
                    minm = amin(listvarb[k][indxsampspmrtemp][where(listvarb[k][indxsampspmrtemp] > 0.)])
                    bins = logspace(log10(minm), log10(maxm), 40)
                else:
                    minm = amin(listvarb[k][indxsampspmrtemp])
                    bins = linspace(minm, maxm, 40)
              
                try:
                    axis.hist(listvarb[k][indxsampsplttemp], bins=bins, label='Split', alpha=gdat.alphmrkr)
                    axis.hist(listvarb[k][indxsampmerg], bins=bins, label='Merge', alpha=gdat.alphmrkr)
                except:
                    if gdat.verbtype > 0:
                        print 'Skipping split merge diagnostic plot...'
                axis.set_ylabel('$N_{samp}$')
                axis.set_xlabel(listlabl[k])
                axis.legend()
                plt.tight_layout()
                plt.savefig(gdat.pathplot + 'spmr/' + listname[k] + '.pdf')
                plt.close(figr)
    
    if gdat.verbtype > 0:
        print 'Calculating proposal execution times...'
    timeinit = gdat.functime()
    plot_chro(gdat)
    timefinl = gdat.functime()
    if gdat.verbtype > 0:
        print 'Done in %.3g seconds.' % (timefinl - timeinit)

    numbpntspost = 3
    # temp -- posterior plots only work for numbcompcolr == 4
    if gdat.strgcnfg == 'test_post' and gdat.datatype == 'mock' and gdat.mocknumbpnts[0] == numbpntspost and gdat.numbpopl == 1 and gdat.numbback == 1:
        if gdat.verbtype > 0:
            print 'Making the grid posterior plot...'
        timeinit = gdat.functime()
   
        numbpara = numbpntspost * gdat.numbcompcolr + gdat.numbener
        listpost = zeros((gdat.numbsamp, numbpara))
        for j in gdat.indxsamptotl:
            for k in range(numbpntspost):
                listpost[j, 0*numbpntspost+k] = gdat.listlgal[0][j][k]
                listpost[j, 1*numbpntspost+k] = gdat.listbgal[0][j][k]
                listpost[j, 2*numbpntspost+k] = gdat.listspec[0][j][gdat.indxenerfluxdist[0], k]
                listpost[j, 3*numbpntspost+k] = gdat.listspep[0][j][k, :]
        for i in gdat.indxener:
            listpost[:, 4*numbpntspost+i] = gdat.listbacp[:, 0, i]
        truepost = zeros(numbpara)
        truepost[0*numbpntspost:1*numbpntspost] = gdat.truelgal[0][k]
        truepost[1*numbpntspost:2*numbpntspost] = gdat.truebgal[0][k]
        truepost[2*numbpntspost:3*numbpntspost] = gdat.truespec[0][0, gdat.indxenerfluxdist[0], k]
        truepost[3*numbpntspost:4*numbpntspost] = gdat.truespep[0][k, 0]
        truepost[4*numbpntspost:] = gdat.truebacp[0, :]
        path = gdat.pathplot + 'postdist'
        strgpara = ['$%s_%d$' % (strg, indxpnts + 1) for strg in ['l', 'b', 'f', 's'] for indxpnts in arange(numbpnts)]
        strgpara += ['$A_{%d}$' % i for i in gdat.indxener]
        
        tdpy.mcmc.plot_grid(path, listpost, strgpara, truepara=truepost, numbtickbins=3)

        # find the matrix of partial derivatives
        ## evaluate the likelihood at the sample
        # temp
        #gdatmodi = tdpy.util.gdatstrt()
        #retr_llik(gdat, gdatmodi, init=True)

        ## evaluate the likelihood at the vicinity of the sample
        #for a in range():
        #    for b in range():
        #        retr_llik(gdat, gdatmodi)

        timefinl = gdat.functime()
        if gdat.verbtype > 0:
            print 'Done in %.3g seconds.' % (timefinl - timeinit)

    # stacked posteiors binned in position and flux
    if gdat.numbtrap > 0:
        liststrgbins = ['quad', 'full', 'cumu']
        for l in gdat.indxpopl:
            liststrgfluxspep = gdat.liststrgfluxspep[l]
            for strgbins in liststrgbins:
                for strgfluxspep in liststrgfluxspep:
                    plot_pntsprob(gdat, l, strgbins, strgfluxspep)

    # posterior versions of the frame plots
    plot_samp(gdat)
    
    ## mosaic of images of posterior catalogs 
    plot_mosa(gdat)
   
    ## fixed-dimensional parameters
    ### trace plot for each parameter
    for k in gdat.indxfixp:
        if k in gdat.indxfixpactv:
            path = gdat.pathpost + gdat.namefixp[k]
            tdpy.mcmc.plot_trac(path, gdat.listfixp[:, k], gdat.strgfixp[k], truepara=gdat.truefixp[k])
    ### full covariance plot
    path = gdat.pathpost + 'fixp'
    tdpy.mcmc.plot_grid(path, gdat.listfixp[:, gdat.indxfixpactv] * gdat.factfixpplot[None, gdat.indxfixpactv], gdat.strgfixp[gdat.indxfixpactv], \
                                                                                      truepara=gdat.truefixp[gdat.indxfixpactv] * gdat.factfixpplot[gdat.indxfixpactv])
    ### grouped covariance plots
    #### hyperparameters
    if gdat.indxfixphypractv.size > 0:
        path = gdat.pathpost + 'hypr'
        tdpy.mcmc.plot_grid(path, gdat.listfixp[:, gdat.indxfixphypractv], gdat.strgfixp[gdat.indxfixphypractv], truepara=[gdat.truefixp[k] for k in gdat.indxfixphypractv])
    #### PSF
    if gdat.proppsfp:
        path = gdat.pathpost + 'psfp'
        tdpy.mcmc.plot_grid(path, gdat.listfixp[:, gdat.indxfixppsfp], gdat.strgfixp[gdat.indxfixppsfp], truepara=[gdat.truefixp[k] for k in gdat.indxfixppsfp], \
                                                                                                                                        numbplotside=gdat.numbpsfptotl)
    #### backgrounds
    if gdat.propbacp:
        path = gdat.pathpost + 'bacp'
        tdpy.mcmc.plot_grid(path, gdat.listfixp[:, gdat.indxfixpbacp.flatten()], gdat.strgfixp[gdat.indxfixpbacp.flatten()], \
                                                                                                        truepara=[gdat.truefixp[k] for k in gdat.indxfixpbacp.flatten()])
        if gdat.indxfixpbacp.size == 2:
            tdpy.mcmc.plot_grid(path, gdat.listfixp[:, gdat.indxfixpbacp.flatten()], gdat.strgfixp[gdat.indxfixpbacp.flatten()], \
                                                                            truepara=[gdat.truefixp[k] for k in gdat.indxfixpbacp.flatten()], join=True)
    
    ## randomly selected trandimensional parameters
    if gdat.numbtrap > 0:
        numbtrapplot = min(10, gdat.numbtrap)
        indxtrapplot = sort(choice(gdat.indxsampcomp, size=numbtrapplot, replace=False))
        path = gdat.pathpost + 'listsamp'
        print 'gdat.listsamp'
        print gdat.listsamp
        print 'indxtrapplot'
        print indxtrapplot
        tdpy.mcmc.plot_grid(path, gdat.listsamp[:, indxtrapplot], ['%d' % k for k in indxtrapplot])

    ## log-prior and log-likelihood
    for strg in ['llik', 'lpri']:

        if strg == 'llik':
            labltemp = '\ln P(x)'
        if strg == 'lpri':
            labltemp = '\ln P(D|x)'
        
        setattr(gdat, 'list' + strg + 'flat', getattr(gdat, 'list' + strg).flatten())
        setattr(gdat, 'listdelt' + strg + 'flat', getattr(gdat, 'listdelt' + strg).flatten())
        
        labl = r'$%s$' % labltemp
        labldelt = r'$\Delta%s$' % labltemp

        path = gdat.pathpost + strg
        titl = r'$D_{KL} = %.5g, \ln P(D) = %.5g$' % (gdat.info, gdat.levi)
        tdpy.mcmc.plot_hist(path, getattr(gdat, 'list' + strg + 'flat'), labl, titl)
        if strg == 'llik':
            varbdraw = [gdat.maxmllikswep]
            labldraw = ['Maximum likelihood Sample']
        else:
            varbdraw = None
            labldraw = None
        tdpy.mcmc.plot_trac(path, getattr(gdat, 'list' + strg + 'flat'), labl, varbdraw=varbdraw, labldraw=labldraw)

        pathpostdelt = gdat.pathpost + 'delt' + strg + '/'
        pathpostdeltaccp = pathpostdelt + 'accp/'
        pathpostdeltreje = pathpostdelt + 'reje/'
        for path in [pathpostdelt, pathpostdeltaccp, pathpostdeltreje]:
            os.system('mkdir -p %s' % path)

        path = pathpostdelt + 'delt' + strg
        tdpy.mcmc.plot_trac(path, getattr(gdat, 'listdelt' + strg + 'flat'), labldelt)
        if gdat.numbproc > 1:
            path = pathpostdelt + 'delt' + strg + 'proc'
            tdpy.mcmc.plot_trac(path, getattr(gdat, 'listdelt' + strg), labldelt, titl='All processes')
        for n in gdat.indxprop:
            path = pathpostdelt + 'delt%s_%s' % (strg, gdat.nameprop[n])
            tdpy.mcmc.plot_trac(path, getattr(gdat, 'listdelt' + strg + 'flat')[gdat.listindxsamptotlprop[n]], labldelt, titl=gdat.strgprop[n])
            path = pathpostdeltaccp + 'delt%s_%s_accp' % (strg, gdat.nameprop[n])
            tdpy.mcmc.plot_trac(path, getattr(gdat, 'listdelt' + strg + 'flat')[gdat.listindxsamptotlpropaccp[n]], labldelt, titl=gdat.strgprop[n] + ', Accepted')
            path = pathpostdeltreje + 'delt%s_%s_reje' % (strg, gdat.nameprop[n])
            tdpy.mcmc.plot_trac(path, getattr(gdat, 'listdelt' + strg + 'flat')[gdat.listindxsamptotlpropreje[n]], labldelt, titl=gdat.strgprop[n] + ', Rejected')
        
    # plot resident memory
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    axis.plot(gdat.indxsamp, mean(gdat.listmemoresi, 1) / float(2**30))
    axis.set_ylabel(r'$M$ [GB]')
    axis.set_xlabel(r'$i_{samp}$')
    plt.tight_layout()
    plt.savefig(gdat.pathdiag + 'memoresi.pdf')
    plt.close(figr)

    # animate the frame plots
    if gdat.makeanim:
        make_anim(gdat)

    timetotlfinl = gdat.functime()
    if gdat.verbtype > 0:
        print 'Plots and animations are produced in %.3g seconds.' % (timetotlfinl - timetotlinit)


def plot_chro(gdat):

    if amin(gdat.listchrototl <= 0.) or amin(gdat.listchrollik <= 0.):
        print 'Invalid chronometer...'

    gdat.listchrototl *= 1e3
    binstime = logspace(log10(amin(gdat.listchrototl[where(gdat.listchrototl > 0)])), log10(amax(gdat.listchrototl)), 50)
    figr, axcl = plt.subplots(gdat.numbprop, 1, figsize=(2 * gdat.plotsize, gdat.numbprop * gdat.plotsize / 3.))
    if gdat.numbprop == 1:
        axcl = [axcl]
    for k in gdat.indxprop:
        indxswepchro = intersect1d(gdat.listindxsamptotlprop[k], where(gdat.listchrototl[:, 0] > 0)[0])
        try:
            axcl[k].hist(gdat.listchrototl[indxswepchro, 0], binstime, log=True, label=gdat.strgprop[k])
        except:
            pass
        axcl[k].set_xlim([amin(binstime), amax(binstime)])
        axcl[k].set_ylim([0.5, None])
        axcl[k].set_ylabel(gdat.strgprop[k])
        axcl[k].set_xscale('log')
        if k != gdat.numbprop - 1:
            axcl[k].set_xticklabels([])
    axcl[-1].set_xlabel('$t$ [ms]')
    plt.subplots_adjust(hspace=0.05)
    plt.savefig(gdat.pathdiag + 'chroprop.pdf')
    plt.close(figr)

    labl = ['Total', 'Proposal', 'Prior', 'Likelihood', 'Save', 'Rest']
    listcolr = ['black', 'b', 'g', 'r', 'y', 'm']
    numblabl = len(labl)
    figr, axcl = plt.subplots(2, 1, figsize=(2 * gdat.plotsize, gdat.plotsize))
    for k in range(numblabl - 1):
        if k == numblabl - 2:
            varb = gdat.listchrototl[:, 0] - sum(gdat.listchrototl[:, 1:], 1)
        else:
            varb = gdat.listchrototl[:, k+1]
        try:
            axcl[0].hist(varb, binstime, log=True, label=labl[k+1], alpha=0.5, color=listcolr[k+1])
        except:
            pass
    axcl[1].hist(gdat.listchrototl[:, 0], binstime, log=True, label=labl[0], color=listcolr[0], alpha=0.5)
    axcl[1].set_title(r'$\langle t \rangle$ = %.3g ms' % mean(gdat.listchrototl[where(gdat.listchrototl[:, 0] > 0)[0], 0]))
    axcl[0].set_xlim([amin(binstime), amax(binstime)])
    axcl[1].set_xlim([amin(binstime), amax(binstime)])
    axcl[0].set_xscale('log')
    axcl[1].set_xscale('log')
    axcl[0].set_ylim([0.5, None])
    axcl[1].set_ylim([0.5, None])
    axcl[0].legend(loc=9, ncol=len(labl)-1)
    axcl[1].legend(loc=2)
    axcl[0].set_xticklabels([])
    axcl[1].set_xlabel('$t$ [ms]')
    plt.subplots_adjust(bottom=0.15, hspace=0.18)
    plt.savefig(gdat.pathdiag + 'chrototl.pdf')
    plt.close(figr)

    gdat.listchrollik *= 1e3
   
    if (gdat.listchrollik != 0).any():
        listlabl = ['PSF Intp.', 'Variables', 'Pixel mesh', 'Energy mesh', 'PS flux', 'Total flux', 'Lens host', 'Lens source', 'PSF conv.', 'Counts', 'Unbinned', 'Likelihood']
        numblabl = len(listlabl)
        figr, axcl = plt.subplots(gdat.numbchrollik, 1, figsize=(2 * gdat.plotsize, gdat.plotsize * numblabl / 3.))
        maxmchrollik = amax(gdat.listchrollik)
        minmchrollik = amin(gdat.listchrollik[where(gdat.listchrollik > 0)])
        binstime = logspace(log10(minmchrollik), log10(maxmchrollik), 50)
    
        for k in range(gdat.numbchrollik):
            chro = gdat.listchrollik[where(gdat.listchrollik[:, k] > 0)[0], k]
            try:
                axcl[k].hist(chro, binstime, log=True, label=listlabl[k])
            except:
                pass
            axcl[k].set_xlim([amin(binstime), amax(binstime)])
            axcl[k].set_ylim([0.5, None])
            axcl[k].set_ylabel(listlabl[k])
            axcl[k].set_xscale('log')
            if k != gdat.numbchrollik - 1:
                axcl[k].set_xticklabels([])
            axcl[k].axvline(mean(chro), ls='--', alpha=0.2, color='black')
        axcl[-1].set_xlabel('$t$ [ms]')
        plt.subplots_adjust(hspace=0.05)
        plt.savefig(gdat.pathdiag + 'chrollik.pdf')
        plt.close(figr)


def plot_compfrac(gdat, gdatmodi):
    
    listydat = empty((gdat.numblablcompfrac, gdat.numbener))
    listyerr = zeros((2, gdat.numblablcompfrac, gdat.numbener))
    
    ## data
    listydat[0, :] = gdat.datafluxmean
    cntr = 1
    
    ## total model
    if gdat.numblablcompfrac > 2:
        listydat[cntr, :] = sum(retr_varb(gdat, 'fixp', gdatmodi)[gdat.indxfixpbacp] * gdat.backfluxmean, 0)
        if gdatmodi == None:
            listyerr[:, cntr, :] = mean(retr_varb(gdat, 'fixp', gdatmodi, perc='errr')[:, gdat.indxfixpbacp] * gdat.backfluxmean, 0)
        cntr += 1

    ## PS
    if gdat.pntstype == 'lght':
        if gdatmodi == None:
            listydat[cntr, :] = gdat.medipntsfluxmean
            listyerr[:, cntr, :] = gdat.errrpntsfluxmean
        else:
            listydat[cntr, :] = gdatmodi.thispntsfluxmean
        cntr += 1
    
    ## background templates
    for c in gdat.indxback:
        listydat[cntr+c, :] = retr_varb(gdat, 'fixp', gdatmodi)[gdat.indxfixpbacp[c]] * gdat.backfluxmean[c, :]
        if gdatmodi == None:
            listyerr[:, cntr+c, :] = retr_varb(gdat, 'fixp', gdatmodi, perc='errr')[:, gdat.indxfixpbacp[c]] * gdat.backfluxmean[c, :]
    
    # plot energy spectra of the data, background model components and total background
    if gdat.numbener > 1:
        figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
       
        xdat = gdat.enerfact * gdat.meanener
        for k in range(gdat.numblablcompfrac):
            
            print 'gdat.listlablcompfrac'
            print gdat.listlablcompfrac[k]
            print 'listydat'
            print listydat[k, :]
            print 

            ydat = gdat.meanener**2 * listydat[k, :]
            yerr = gdat.meanener**2 * listyerr[:, k, :]
            axis.errorbar(xdat, ydat, yerr=yerr, marker='o', markersize=5, label=gdat.listlablcompfrac[k])
    
        axis.set_xlim([gdat.enerfact * amin(gdat.binsener), gdat.enerfact * amax(gdat.binsener)])
        axis.set_yscale('log')
        axis.set_xlabel('$E$ [%s]' % gdat.strgenerunit)
        axis.set_xscale('log')
        axis.set_ylabel('$E^2dN/dAdtd\Omega dE$ [%s/cm$^2$/s/sr]' % gdat.strgenerunit)
        axis.legend()
    
        plt.tight_layout()
        path = retr_plotpath(gdat, 'compfracspec', gdatmodi)
        plt.savefig(path)
        plt.close(figr)
   
    # pie plot illustrating contribution of each background template (and PS) to the total model
    if gdat.numblablcompfrac > 2:
        numbplot = gdat.numblablcompfrac - 2
    else:
        numbplot = gdat.numblablcompfrac - 1
    listexpl = zeros(numbplot)
    listexpl[0] = 0.1
    listsize = zeros(numbplot)
    for k in range(numbplot):
        # temp -- this is wrong -- need to sum
        if gdat.numbener > 1:
            listsize[k] = trapz(listydat[k+1, :], gdat.meanener)
        else:
            listsize[k] = listydat[k+1, :]
   
    if gdat.strgcnfg == 'pcat_ferm_mock_ngal':
        print 'hey'
        print 'listsize'
        print listsize
    listsize *= 100. / sum(listsize)
    if gdat.strgcnfg == 'pcat_ferm_mock_ngal':
        print 'listsize'
        print listsize
        
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))

    labl = ['PS'] + gdat.lablback
   
    if gdat.strgcnfg == 'pcat_ferm_mock_ngal':
        print 'listydat'
        print listydat
        print 

    axis.pie(listsize, explode=listexpl, labels=labl, autopct='%1.1f%%')
    axis.axis('equal')

    plt.subplots_adjust(top=0.8, bottom=0.2, left=0.2, right=0.8)
    path = retr_plotpath(gdat, 'compfrac', gdatmodi)
    plt.savefig(path)
    plt.close(figr)
     

def plot_histsind(gdat, l, gdatmodi):
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    if gdatmodi == None:
        xdat = gdat.meansind
        ydat = gdat.medispephist[l][0, :]
        yerr = gdat.errrspephist[l][:, 0, :]
        axis.errorbar(xdat, ydat, ls='', yerr=yerr, lw=1, marker='o', markersize=5, color='black')
    else:
        try:
            axis.hist(gdatmodi.thissampvarb[gdatmodi.thisindxsampspep[l][gdatmodi.indxmodlpntscomp[l], 0]], gdat.binssind, alpha=gdat.alphmrkr, color='b', \
                                                                                                                                                log=True, label='Sample')
        except:
            print 'Skipping the plot of color histogram...'
            print 'gdat.binssind'
            print gdat.binssind
            print 'thisspep'
            print gdatmodi.thissampvarb[gdatmodi.thisindxsampspep[l][gdatmodi.indxmodlpntscomp[l]]]
    if gdat.trueinfo and gdat.trueindxpntscomp[l].size > 0 and gdat.truespep[l] != None:
        axis.hist(gdat.truespep[l][gdat.trueindxpntscomp[l], 0], gdat.binssind, alpha=gdat.alphmrkr, color='g', log=True, label=gdat.truelabl)
        if gdat.datatype == 'mock' and gdat.exprinfo and gdat.exprspep != None:
            axis.hist(gdat.exprspep[:, 0], gdat.binssind, alpha=gdat.alphmrkr, color='red', log=True, label=gdat.strgcatl)
    axis.set_yscale('log')
    axis.set_xlabel('$s$')
    axis.set_xlim([gdat.minmsind, gdat.maxmsind])
    axis.set_ylabel('$N$')
    axis.set_ylim(gdat.limshist)
    axis.legend(loc=2)
    
    plt.tight_layout()
    path = retr_plotpath(gdat, 'histsind_pop%d' % l, gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    

def plot_pdfntotlflux():

    minm = 1e-9
    maxm = 10e-9
    numbvarb = 90
    numbsamp = 100000
    numbbins = 40
    alph = 0.5
    
    binssing = linspace(minm, maxm, numbvarb + 1)
    meansing = (binssing[:-1] + binssing[1:]) / 2.
    deltsing = binssing[1:] - binssing[:-1]
    
    binsdoub = linspace(2. * minm, 2. * maxm, 2 * numbvarb)
    meandoub = (binsdoub[:-1] + binsdoub[1:]) / 2.
    deltdoub = binsdoub[1:] - binsdoub[:-1]
    
    bins = linspace(minm, 2. * maxm, 2 * numbvarb + 1)
    
    arry = empty((2, numbsamp))
    
    minmslop = 1.5
    maxmslop = 3.
    numbslop = 4
    sloparry = linspace(minmslop, maxmslop, numbslop)
    for n in range(numbslop):
        slop = sloparry[n]
        for k in range(2):
            arry[k, :] = (rand(numbsamp) * (maxm**(1. - slop) - minm**(1. - slop)) + minm**(1. - slop))**(1. / (1. - slop))
        
        totl = sum(arry, 0)
        
        powrprob = (1. - slop) / (maxm**(1. - slop) - minm**(1. - slop)) * meansing**(-slop)
        
        convprob = convolve(powrprob, powrprob) * deltdoub[0]
        
        indxdoub = where(meandoub <= maxm)[0]
        convprobpoly = polyval(polyfit(meandoub[indxdoub], convprob[indxdoub], 8), meandoub[indxdoub])
        
        figr, axis = plt.subplots()
        axis.hist(arry[k, :], bins=bins, alpha=alph, label='$f_1$ (Sampled)', color='b')
        axis.hist(totl, bins=bins, alpha=alph, label='$f_0$ (Sampled)', color='g')
        axis.plot(meansing, powrprob * numbsamp * deltsing, label='$f_1$ (Analytic)', color='b')
        axis.plot(meandoub, convprob * numbsamp * deltdoub[0], label='$f_0$ (Numerically convolved)', color='g')
        
        axis.plot(meandoub[indxdoub], convprobpoly * numbsamp * deltdoub[indxdoub], label='$f_0$ (Fit)', color='r')
    
        axis.set_ylim([0.5, numbsamp])
        axis.set_xlabel('$f$')
        axis.set_xlim([amin(bins), amax(bins)])
        axis.set_xscale('log')
        axis.set_yscale('log')
        axis.set_ylabel('$N_{samp}$')
        axis.legend()
        plt.tight_layout()
        pathfold = os.environ["TDGU_DATA_PATH"] + '/imag/powrpdfn/'
        os.system('mkdir -p ' + pathfold)
        plt.savefig(pathfold + 'powrpdfn%04d.pdf' % n)
        plt.close(figr)
        

def plot_brgt(gdat, gdatmodi):
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    if gdatmodi == None:
        # temp
        pass
    else:   
        fluxbrgt, fluxbrgtassc = retr_fluxbrgt(gdat, gdatmodi.thissampvarb[concatenate(gdatmodi.thisindxsamplgal)], \
                                                                         gdatmodi.thissampvarb[concatenate(gdatmodi.thisindxsampbgal)], \
                                                                         gdatmodi.thissampvarb[concatenate(gdatmodi.thisindxsampspec)[gdat.indxenerfluxdist[0], :]])
        if fluxbrgt.size > 0:
            axis.scatter(fluxbrgt, fluxbrgtassc, alpha=gdat.alphmrkr, color='b', label='Sample')
            axis.scatter(fluxbrgt[0], sum(fluxbrgtassc), alpha=gdat.alphmrkr, color='b', label='Sample - Total')
    if gdat.trueinfo:
        if gdat.truefluxbrgt.size > 0:
            axis.scatter(gdat.truefluxbrgt, gdat.truefluxbrgtassc, alpha=gdat.alphmrkr, color='g', label=gdat.truelabl)
        if gdat.datatype == 'mock' and gdat.exprinfo and gdat.exprlgal.size > 0:
            axis.scatter(gdat.exprfluxbrgt, gdat.exprfluxbrgtassc, alpha=gdat.alphmrkr, color='red', label=gdat.strgcatl)
    axis.set_xscale('log')
    axis.set_xlabel(r'$%s_{assc}$' % gdat.strgflux)
    axis.set_xlim([gdat.minmfluxplot, gdat.maxmfluxplot])
    axis.set_ylim([gdat.minmfluxplot, gdat.maxmfluxplot])
    axis.set_ylabel(r'$%s_{max}$' % gdat.strgflux)
    axis.legend(loc=2)
    
    plt.tight_layout()
    path = retr_plotpath(gdat, 'scatbrgt', gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    

def plot_fluxsind(gdat, l, gdatmodi, strgtype):
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    if gdatmodi == None:
        
        #ydat = gdat.medispephist[l][0, :]
        #yerr = gdat.errrspephist[l][:, 0, :]
        #axis.hist2d(flux, sind, [gdat.binsfluxplot, gdat.binssind], color='b', alpha=gdat.alphmrkr)
        
        #imag = axis.imshow(gdat.medifluxspephist[l][0, :], cmap='Purples', extent=[])
        imag = axis.pcolor(gdat.binsfluxplot, gdat.binssind, gdat.medifluxspephist[l][0, :], cmap='Purples')

        #cset = plt.contour(gdat.medifluxspephist[l][0, :], np.arange(-1, 1.5, 0.2), linewidths=2, cmap='Blues', \
        #                                                        extent=[amin(gdat.binsfluxplot), amax(gdat.binsfluxplot), amin(gdat.binssind), amax(gdat.binssind)])
        #plt.clabel(cset, inline=True, fmt='%1.1f', fontsize=10)
        plt.colorbar(imag) 

    else:
        flux = gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l][gdat.indxenerfluxdist[0], :]]
        sind = gdatmodi.thissampvarb[gdatmodi.thisindxsampspep[l][:, 0]]
        if strgtype == 'hist':
            print 'flux'
            print flux
            print 'sind'
            print sind
            print 'gdat.binsfluxplot'
            print gdat.binsfluxplot
            print 'gdat.binssind'
            print gdat.binssind
            print
            axis.hist2d(flux, sind, [gdat.binsfluxplot, gdat.binssind], cmap='Blues', alpha=gdat.alphmrkr)
            #hist = histogram2d(flux, sind, bins=[gdat.binsfluxplot, gdat.binssind])[0]
            #axis.pcolor(gdat.binsfluxplot, gdat.binssind, hist, cmap='Blues', label='Sample',  alpha=gdat.alphmrkr)
        else:
            axis.scatter(flux, sind, alpha=gdat.alphmrkr, color='b', label='Sample')
    
    if gdat.trueinfo and gdat.truespep[l] != None:
        if False:
            axis.hist2d(gdat.truespec[l][0, gdat.indxenerfluxdist[0], :], gdat.truespep[l][:, 0], [gdat.binsfluxplot, gdat.binssind], cmap='Greens', alpha=gdat.alphmrkr)
            #hist = histogram2d(gdat.truespec[l][0, gdat.indxenerfluxdist[0], :], gdat.truespep[l][:, 0], bins=[gdat.binsfluxplot, gdat.binssind], )[0]
            #axis.pcolor(gdat.binsfluxplot, gdat.binssind, hist, cmap='Greens', label=gdat.truelabl,  alpha=gdat.alphmrkr)
        else:
            axis.scatter(gdat.truespec[l][0, gdat.indxenerfluxdist[0], :], gdat.truespep[l][:, 0], alpha=gdat.alphmrkr, color='g', label=gdat.truelabl)
        if gdat.datatype == 'mock' and gdat.exprinfo and gdat.exprspep != None:
            if False:
                axis.hist2d(gdat.exprspec[0, gdat.indxenerfluxdist[0], :], gdat.exprspep[:, 0], [gdat.binsfluxplot, gdat.binssind], cmap='Reds', \
                                                                                                                    alpha=gdat.alphmrkr, label=gdat.nameexpr)
                #hist = histogram2d(gdat.exprspec[0, gdat.indxenerfluxdist[0], :], gdat.exprsind, bins=[gdat.binsfluxplot, gdat.binssind])[0]
                #axis.pcolor(gdat.binsfluxplot, gdat.binssind, hist, color='Reds', label=gdat.nameexpr, alpha=gdat.alphmrkr)
            else:
                axis.scatter(gdat.exprspec[0, gdat.indxenerfluxdist[0], :], gdat.exprspep[:, 0], alpha=gdat.alphmrkr, color='r', label=gdat.nameexpr)
    axis.set_xscale('log')
    axis.set_xlabel('$%s$ [%s]' % (gdat.strgflux, gdat.strgfluxunit))
    axis.set_ylabel('$s$')
    axis.set_xlim([gdat.minmfluxplot, gdat.maxmfluxplot])
    axis.set_ylim([gdat.minmsind, gdat.maxmsind])
    axis.legend(loc=2)

    plt.tight_layout()
    path = retr_plotpath(gdat, '%sfluxsind_pop%d' % (strgtype, l), gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    

def plot_histspec(gdat, l, gdatmodi, plotspec=False):
  
    if gdat.pixltype != 'unbd' and gdat.pntstype == 'lght':
        if gdatmodi == None:
            binssigm = gdat.medibinssigm
        else:
            binssigm = gdatmodi.binssigm

    if plotspec:
        numbcols = gdat.numbener
    else:
        numbcols = 1

    figr, axcl = plt.subplots(1, numbcols, figsize=(gdat.plotsize * numbcols, gdat.plotsize))
    if plotspec:
        indxenertemp = gdat.indxener
    else:
        indxenertemp = gdat.indxenerfluxdist
        axcltemp = []
        for i in gdat.indxener:
            if i == gdat.indxenerfluxdist:
                axcltemp.append(axcl)
            else:
                axcltemp.append(None)
        axcl = axcltemp
    
    for i in indxenertemp:
        axis = axcl[i]
        if gdatmodi == None:
            xdat = gdat.fluxfactplot * gdat.meanspecplot[i, :]
            ydat = gdat.medispechist[l, :, i]
            yerr = gdat.errrspechist[:, l, :, i]
            axis.errorbar(xdat, ydat, ls='', yerr=yerr, lw=1, marker='o', markersize=5, color='black')
        
            # superimpose posterior on the flux hyperprior
            ydat = gdat.listfluxhistprio
            tdpy.util.plot_braz(axis, xdat, ydat, lcol='lightgrey', dcol='grey', labl='Flux prior')

        else:
            spec = gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l]][i, gdatmodi.indxmodlpntscomp[l]]
            # temp -- gdat.binsspecplot may be too narrow if there are many energy bins or PS colors are extreme
            try:
                axis.hist(gdat.fluxfactplot * spec, gdat.fluxfactplot * gdat.binsspecplot[i, :], alpha=gdat.alphmrkr, color='b', log=True, label='Sample')
            except:
                print 'Spectral bins are inappropriate. Skipping the spectral histogram...'
            
            # superimpose the current prior flux distribution
            if i == gdat.indxenerfluxdist[0]:
                fluxhistprio = retr_fluxhistprio(gdat, l, gdatmodi.thissampvarb)
                axis.plot(gdat.fluxfactplot * gdat.meanspecplot[i, :], fluxhistprio, ls='--', alpha=gdat.alphmrkr, color='b')

        if gdat.pntstype == 'lens':
            axiscnts = axis.twiny()
            axiscnts.set_xscale('log')
            axiscnts.set_xlabel(r'$M$ [$M_{\odot}$]')
            axiscnts.spines['bottom'].set_position(('axes', 1.))
            axiscnts.set_xlim([gdat.minmmass, gdat.maxmmass])
            axiscnts.xaxis.set_ticks_position('bottom')
            axiscnts.xaxis.set_label_position('bottom')
           
        if gdat.pixltype != 'unbd' and gdat.pntstype == 'lght':
            # add another horizontal axis for counts
            axiscnts = axis.twiny()
            axiscnts.set_xscale('log')
            axiscnts.set_xlabel('$C$')
            axiscnts.spines['bottom'].set_position(('axes', 1.))
            axiscnts.set_xlim([gdat.binscnts[i, 0], gdat.binscnts[i, -1]])
            axiscnts.xaxis.set_ticks_position('bottom')
            axiscnts.xaxis.set_label_position('bottom')
           
            # temp
            if False:
                # add yet another horizontal axis for fluctuation significance
                axissigm = axis.twiny()
                axissigm.set_xscale('log')
                axissigm.set_xlabel(r'$\sigma$')
                axissigm.spines['top'].set_position(('axes', 1.05))
                axissigm.set_xlim([binssigm[i, 0], binssigm[i, -1]])
                axissigm.axvline(1., ls='--', alpha=0.1)
                axissigm.axvline(5., ls='--', alpha=0.1)
        
        if gdat.pntstype == 'lens':
            
            if gdatmodi == None:
                axis.axvline(gdat.postfixp[0, gdat.indxfixpbeinhost] * gdat.fluxfactplot, color='b', alpha=0.3)
            else:
                axis.axvline(gdatmodi.thissampvarb[gdat.indxfixpbeinhost] * gdat.fluxfactplot, color='b', alpha=0.3)
            axis.axvline(gdat.truefixp[gdat.trueindxfixpbeinhost] * gdat.fluxfactplot, color='g', ls='--', alpha=0.3)
            
            axis.set_xlim([gdat.fluxfactplot * gdat.minmspecplot[i], 2. * gdat.fluxfactplot * gdat.maxmfixp[gdat.indxfixpbeinhost]])
        else:
            axis.set_xlim([gdat.fluxfactplot * gdat.minmspecplot[i], gdat.fluxfactplot * gdat.maxmspecplot[i]])

        # superimpose the true catalog
        if gdat.trueinfo and gdat.trueindxpntscomp[l].size > 0:
            truehist = axis.hist(gdat.fluxfactplot * gdat.truespec[l][0, i, gdat.trueindxpntscomp[l]], gdat.fluxfactplot * gdat.binsspecplot[i, :], alpha=gdat.alphmrkr, \
                                                                                                                            color='g', log=True, label=gdat.truelabl)
            if gdat.datatype == 'mock' and gdat.exprinfo:
                axis.hist(gdat.fluxfactplot * gdat.exprspec[0, i, :], gdat.fluxfactplot * gdat.binsspecplot[i, :], color='red', alpha=gdat.alphmrkr, log=True, label=gdat.strgcatl)
        
        axis.set_yscale('log')
        axis.set_xlabel('$%s$%s' % (gdat.strgflux, gdat.strgfluxunitextn))
        axis.set_xscale('log')
        if gdat.enerbins:
            axis.text(0.75, 0.65, gdat.strgbinsener[i], ha='center', va='center', transform=axis.transAxes)
        axis.set_ylim(gdat.limshist)
        if plotspec:
            if i == 0:
                axis.set_ylabel('$N$')
            if i == numbcols / 2:
                axis.legend()
        else:
            axis.set_ylabel('$N$')
            axis.legend(loc=7)
    
    plt.tight_layout()
    if plotspec:
        strg = 'spec'
    else:
        strg = 'flux'
    path = retr_plotpath(gdat, 'hist%s%d' % (strg, l), gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    

def plot_gene(gdat, gdatmodi, strgplot, strgxdat, scal=None, scalxaxi=None, scalyaxi=None, lablxaxi='', lablyaxi=''):
    
    if scal == None:
        if scalxaxi == None:
            scalxaxi = 'linr'
        if scalyaxi == None:
            scalyaxi = 'linr'
    else:
        scalxaxi = scal
        scalyaxi = scal

    figr, axis = plt.subplots(figsize=(gdat.plotsize * gdat.numbener, gdat.plotsize))

    xdat = getattr(gdat, 'mean' + strgxdat)
    if gdatmodi == None:
        ydat = getattr(gdat, 'medi' + strgplot)
        yerr = getattr(gdat, 'errr' + strgplot)
        axis.errorbar(xdat, ydat, yerr=yerr, marker='o', ls='', color='black', markersize=5)
    else:
        ydat = getattr(gdatmodi, 'this' + strgplot)
        axis.plot(xdat, ydat)

    if scalxaxi == 'logt':
        axis.set_xscale('log')
    if scalyaxi == 'logt':
        axis.set_yscale('log')
    
    axis.set_xlabel(lablxaxi)
    axis.set_ylabel(lablyaxi)

    plt.tight_layout()
    path = retr_plotpath(gdat, strgplot, gdatmodi)
    plt.savefig(path)
    plt.close(figr)


def plot_scatspec(gdat, l, gdatmodi, plotdiff=False):
    
    figr, axrw = plt.subplots(1, gdat.numbener, figsize=(gdat.plotsize * gdat.numbener, gdat.plotsize))
    if gdat.numbener == 1:
        axrw = [axrw]
    for i, axis in enumerate(axrw):

        # prepare data to be plotted
        xdat = copy(gdat.truespec[l][0, i, :])
        xerr = tdpy.util.retr_errrvarb(gdat.truespec[l][:, i, :])
        yerr = zeros((2, xdat.size))
        if gdatmodi == None:
            ydat = copy(gdat.medispecassc[l][i, :])
            yerr = copy(gdat.errrspecassc[l][:, i, :])
        else:
            ydat = gdatmodi.thisspecassc[l][i, :]

        if (ydat == 0.).all():
            continue
            
        # temp -- this is dangerous!!
        xdat *= gdat.fluxfactplot
        xerr *= gdat.fluxfactplot
        ydat *= gdat.fluxfactplot
        yerr *= gdat.fluxfactplot
        
        if plotdiff:
            ydat = 100. * (ydat - xdat) / xdat
       
        # plot all associations
        indx = where(ydat > 0.)[0]
        if indx.size > 0:
            axis.errorbar(xdat[indx], ydat[indx], ls='', yerr=yerr[:, indx], xerr=xerr[:, indx], lw=1, marker='o', markersize=5, color='black', alpha=0.1)
       
        # plot associations inside the comparison area
        indx = intersect1d(where(ydat > 0.)[0], gdat.trueindxpntscomp[l])
        if indx.size > 0:
            axis.errorbar(xdat[indx], ydat[indx], ls='', yerr=yerr[:, indx], xerr=xerr[:, indx], lw=1, marker='o', markersize=5, color='black')
        
        # plot associations to multiple model point sources
        if gdatmodi != None:
            indx = intersect1d(gdatmodi.trueindxpntsassc[l].mult, gdat.trueindxpntscomp[l])
            if len(indx) > 0:
                axis.errorbar(xdat[indx], ydat[indx], ls='', yerr=yerr[:, indx], xerr=xerr[:, indx], lw=1, marker='o', markersize=5, color='r')
    
        if plotdiff:
            axis.axhline(0., ls='--', alpha=gdat.alphmrkr, color='black')
        else:
            if gdat.pntstype == 'lght':
                # superimpose the bias line
                fluxbias = retr_fluxbias(gdat, gdat.binsspecplot[i, :], i)
                axis.plot(gdat.fluxfactplot * gdat.binsspecplot[i, :], gdat.fluxfactplot * gdat.binsspecplot[i, :], ls='--', alpha=gdat.alphmrkr, color='black')
                axis.plot(gdat.fluxfactplot * gdat.binsspecplot[i, :], gdat.fluxfactplot * fluxbias[0, :], ls='--', alpha=gdat.alphmrkr, color='black')
                axis.plot(gdat.fluxfactplot * gdat.binsspecplot[i, :], gdat.fluxfactplot * fluxbias[1, :], ls='--', alpha=gdat.alphmrkr, color='black')
        
        axis.set_xlabel('$%s_{%s}$%s' % (gdat.strgflux, gdat.strgcatl, gdat.strgfluxunitextn))
        if i == 0:
            axis.set_ylabel('$%s_{samp}$ [%s]' % (gdat.strgflux, gdat.strgfluxunit))
        if i == gdat.numbener / 2:
            axis.errorbar(0., 0., ls='', yerr=0., xerr=0., lw=1, marker='o', markersize=5, color='black', alpha=0.1)
            axis.errorbar(0., 0., ls='', yerr=0., xerr=0., lw=1, marker='o', markersize=5, color='black')
            axis.errorbar(0., 0., ls='', yerr=0., xerr=0., lw=1, marker='o', markersize=5, color='r')
            axis.legend(loc=2)
        if not plotdiff:
            axis.set_yscale('log')
        axis.set_xscale('log')
        if gdat.enerbins:
            axis.set_title(gdat.strgbinsener[i])
        if plotdiff:
            limsyaxi = array([-100., 100.])
        else:
            limsyaxi = gdat.fluxfactplot * array([gdat.minmspecplot[i], gdat.maxmspecplot[i]])
        axis.set_ylim(limsyaxi)
        axis.set_xlim([gdat.fluxfactplot * gdat.minmspecplot[i], gdat.fluxfactplot * gdat.maxmspecplot[i]])
        if gdat.enerbins:
            axis.set_title(gdat.strgbinsener[i])
   
    plt.tight_layout()
    if plotdiff:
        strg = 'diff'
    else:
        strg = ''
    path = retr_plotpath(gdat, 'scatspec%s_pop%d' % (strg, l), gdatmodi)
    plt.savefig(path)
    plt.close(figr)


def plot_scatpixl(gdat, gdatmodi):
    
    figr, axgr = plt.subplots(gdat.numbevtt, gdat.numbener, figsize=(gdat.numbener * gdat.plotsize, gdat.numbevtt * gdat.plotsize))
    if gdat.numbevtt == 1:
        axgr = [axgr]
    for m, axrw in enumerate(axgr):
        if gdat.numbener == 1:
            axrw = [axrw]
        for i, axis in enumerate(axrw):
           
            if gdatmodi == None:
                ydat = gdat.medimodlcnts[i, gdat.indxpixlsave, m]
            else:
                ydat = gdatmodi.thismodlcnts[i, gdat.indxpixlsave, m]
            
            axis.scatter(gdat.datacnts[i, gdat.indxpixlsave, m], ydat, alpha=gdat.alphmrkr)

            axislimt = [0., amax(gdat.datacnts[i, :, m]) * 1.5]
            axis.set_xlim(axislimt)
            axis.set_ylim(axislimt)
            
            slop, intc, coef, pval, stdv = sp.stats.linregress(gdat.datacnts[i, gdat.indxpixlsave, m], ydat)
            axis.text(0.5, 0.9, '$m = %.3g, b = %.3g, r = %.3g$' % (slop, intc, coef), va='center', ha='center', transform=axis.transAxes, fontsize=16)
            
            if m == gdat.numbevtt - 1:
                axis.set_xlabel('Data Counts')
            if i == 0:
                labl = 'Model Counts'
                if gdat.evttbins:
                    labl += ', ' + gdat.strgevtt[m]
                axis.set_ylabel(labl)
            if m == 0:
                axis.set_title(gdat.strgbinsener[i])
            
    plt.tight_layout()
    path = retr_plotpath(gdat, 'scatpixl', gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    
    
def plot_indxprox(gdat):

    numbbins = 41
    numbfluxprox = len(gdat.indxpixlprox)
    bins = empty((numbfluxprox, numbbins))
    indxpixlproxsize = empty((numbfluxprox, gdat.numbpixl))
    for h in range(gdat.numbfluxprox):
        for j in gdat.indxpixl:
            indxpixlproxsize[h, j] = gdat.indxpixlprox[h][j].size
        bins[h, :] = logspace(log10(amin(indxpixlproxsize[h, :])), log10(amax(indxpixlproxsize[h, :])), numbbins)
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    for h in range(gdat.numbfluxprox):
        axis.hist(indxpixlproxsize[h, :], bins=bins[h, :], log=True, label='Flux bin %d' % h, alpha=gdat.alphmrkr)
    axis.set_xscale('log')
    axis.axvline(gdat.numbpixl, label='ROI', ls='--')
    axis.set_xlabel('Number of pixels')
    axis.set_ylabel("Number of tables")
    axis.legend(loc=2)
    plt.tight_layout()
    plt.savefig(gdat.pathplot + 'init/indxprox.pdf')
    plt.close()
    
    
def plot_psfn_type():
    
    devi = linspace(0., 5., 100)
    y = zeros((x.size, 5))

    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    singgaus = retr_singgaus(devi, 0.25)
    axis.plot(devi, singgaus, label='Single Gaussian')

    singking = retr_singking(devi, 0.25, 10.)
    axis.plot(devi, singking, label='Single King')

    doubgaus = retr_doubgaus(devi, 0.1, 0.25, 1.)
    axis.plot(devi, doubgaus, label='Double Gaussian')

    gausking = retr_gausking(devi, 0.1, 0.25, 1., 10.)
    axis.plot(devi, gausking, label='Gaussian + King')

    doubking = retr_doubking(devi, 0.1, 0.25, 10., 1., 5.)
    axis.plot(devi, doubking, label='Double King')

    axis.legend()
    axis.set_xscale('log')
    axis.set_yscale('log')
    axis.set_ylim([1e-3, None])
    plt.show()
    
    
def plot_evidtest():
    
    minmgain = -1.
    maxmgain = 5.
    minmdevi = 0.
    maxmdevi = 5.
    gain = linspace(minmgain, maxmgain, 100)
    devi = linspace(minmdevi, maxmdevi, 100)

    evid = log(sqrt(1. + exp(2. * gain[None, :])) * exp(-devi[:, None]**2 / 2. / (1. + 1. / exp(2. * gain[None, :]))))
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    figr.suptitle('Log-Bayesian Evidence For Lower-Dimension Model', fontsize=18)
    imag = axis.imshow(evid, extent=[minmgain, maxmgain, minmdevi, maxmdevi], cmap='winter', origin='lower')
    cset1 = plt.contourf(gain, devi, evid, cmap='winter')
    axis.set_xlabel('Information gain')
    axis.set_ylabel('Goodness of fit')
    plt.colorbar(imag, ax=axis, fraction=0.03)

    plt.tight_layout()
    plt.savefig(gdat.pathplot + 'evidtest.pdf')
    plt.close(figr)
    
    
def plot_pntsprob(gdat, indxpopltemp, strgbins, strgfluxspep):
   
    numbparaplot = getattr(gdat, 'numb' + strgfluxspep + 'plot')

    if strgbins == 'cumu':
        numbrows = 1
        numbcols = 1
    else:
        numbcols = 2
        if strgbins == 'full':
            
            numbrows = numbparaplot / 2
        else:
            numbrows = 2
        
    figr, axgr = plt.subplots(numbrows, numbcols, figsize=(numbcols * gdat.plotsize, numbrows * gdat.plotsize), sharex='all', sharey='all')
    if numbrows == 1:
        axgr = [axgr]            
    for a, axrw in enumerate(axgr):
        if numbcols == 1:
            axrw = [axrw]
        for b, axis in enumerate(axrw):
            h = a * 2 + b
            if strgbins == 'full':
                indxlowr = h
                indxuppr = h + 1
            elif strgbins == 'cumu':
                indxlowr = 0
                indxuppr = numbparaplot
            else:
                if h < 3:
                    indxlowr = 2 * h
                    indxuppr = 2 * (h + 1)
                else:
                    indxlowr = 2 * h
                    indxuppr = numbparaplot
            temp = sum(gdat.pntsprob[indxpopltemp, :, :, indxlowr:indxuppr], 2).T
            if where(temp > 0.)[0].size > 0:
                imag = axis.imshow(temp, interpolation='nearest', origin='lower', cmap='BuPu', extent=gdat.exttrofi, norm=mpl.colors.LogNorm(vmin=0.5, vmax=None))
            else:
                imag = axis.imshow(temp, interpolation='nearest', origin='lower', cmap='BuPu', extent=gdat.exttrofi)
                
            # superimpose true PS
            # temp
            if gdat.trueinfo:
                indxpnts = where((gdat.binsspecplot[gdat.indxenerfluxdist[0], indxlowr] < gdat.truespec[indxpopltemp][0, gdat.indxenerfluxdist[0], :]) & \
                                                    (gdat.truespec[indxpopltemp][0, gdat.indxenerfluxdist[0], :] < gdat.binsspecplot[gdat.indxenerfluxdist[0], indxuppr]))[0]
                mrkrsize = retr_mrkrsize(gdat, gdat.truespec[indxpopltemp][0, gdat.indxenerfluxdist[0], indxpnts])
                axis.scatter(gdat.anglfact * gdat.truelgal[indxpopltemp][indxpnts], gdat.anglfact * gdat.truebgal[indxpopltemp][indxpnts], \
                                                                                        s=mrkrsize, alpha=gdat.alphmrkr, marker='*', lw=2, color='g')
            
            if a == numbrows - 1:
                axis.set_xlabel(gdat.strgxaxitotl)
            else:
                axis.set_xticklabels([])
            if b == 0:
                axis.set_ylabel(gdat.strgyaxitotl)
            else:
                axis.set_yticklabels([])

            draw_frambndr(gdat, axis)
            
            titl = tdpy.util.mexp(gdat.fluxfactplot * gdat.binsspecplot[gdat.indxenerfluxdist, indxlowr]) + ' $< %s <$' % gdat.strgflux + \
                                                                                        tdpy.util.mexp(gdat.fluxfactplot * gdat.binsspecplot[gdat.indxenerfluxdist, indxuppr])
            axis.set_title(titl)
    
    plt.figtext(0.5, 0.95, '$%s$%s' % (gdat.strgflux, gdat.strgfluxunitextn), ha='center', va='center')
    axiscomm = figr.add_axes([0.9, 0.2, 0.02, 0.6])
    cbar = figr.colorbar(imag, cax=axiscomm)

    plt.subplots_adjust(left=0.18, top=.9, right=0.82, bottom=0.15, hspace=0.08, wspace=0.08)
    path = gdat.pathpost + 'pntsbind%s%s%d' % (strgbins, strgfluxspep, indxpopltemp) + '.pdf'
    plt.savefig(path)
    plt.close(figr)
       
    
def plot_king(gdat):

    angl = rad2deg(gdat.binsangl)

    figr, axgr = plt.subplots(1, 2, figsize=(2 * gdat.plotsize, gdat.plotsize))
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
                axis.plot(angl, retr_singking(angl, sigm, gamm), label=r'$\sigma = %.4g, \gamma = %.3g$' % (sigm, gamm))
        axis.legend(loc=lloc)
        axis.set_yscale('log')
        axis.set_xlabel(r'$\theta$%s' % gdat.strganglunit)
        axis.set_xlabel(r'$\mathcal{K}(\theta)$')
        
    plt.tight_layout()
    plt.savefig(gdat.pathplot + 'king.pdf')
    plt.close(figr)
    
    
def plot_psfn(gdat, gdatmodi):
    
    figr, axgr = plt.subplots(gdat.numbevtt, gdat.numbener, figsize=(gdat.numbener * gdat.plotsize, gdat.numbevtt * gdat.plotsize))
    if gdat.numbevtt == 1:
        axgr = [axgr]
    for m, axrw in enumerate(axgr):
        if gdat.numbener == 1:
            axrw = [axrw]
        for i, axis in enumerate(axrw):
            
            if gdatmodi == None:
                if gdat.varioaxi:
                    ydat = gdat.medipsfn[i, :, m, 0]
                    yerr = gdat.errrpsfn[:, i, :, m, 0]
                else:
                    ydat = gdat.medipsfn[i, :, m]
                    yerr = gdat.errrpsfn[:, i, :, m]
                axis.errorbar(gdat.binsanglplot, ydat, ls='', yerr=yerr, lw=1, marker='o', markersize=5, color='black', label='Posterior')
            else:
                if gdat.varioaxi:
                    psfntemp = gdatmodi.thispsfn[i, :, m, 0]
                else:
                    psfntemp = gdatmodi.thispsfn[i, :, m]
                axis.plot(gdat.binsanglplot, psfntemp, label='Sample')
           
            if gdat.truevarioaxi:
                truepsfntemp = gdat.truepsfn[i, :, m, 0]
                truepsfntotltemp = gdat.truepsfn[i, :, m, 0]
            else:
                truepsfntemp = gdat.truepsfn[i, :, m]
                truepsfntotltemp = gdat.truepsfn[i, :, m]

            axis.plot(gdat.binsanglplot, truepsfntemp, label=gdat.nameexpr, color='g', ls='--')
            axis.set_xlim(gdat.limsangl[i][m])
            axis.set_ylim(gdat.limspsfn[i][m])
            axis.set_yscale('log')
                
            if m == gdat.numbevtt - 1:
                labl = r'$\theta$%s' % gdat.strganglunit
                axis.set_xlabel(labl)
            if i == 0 and gdat.evttbins:
                axis.set_ylabel(gdat.strgevtt[m])
            if m == 0 and gdat.enerbins:
                axis.set_title(gdat.strgbinsener[i])  
            if i == gdat.numbener - 1 and m == gdat.numbevtt - 1:
                axis.legend()

            # overplot the PSF parameter values
            if gdatmodi != None:
                indxsamptemp = gdat.indxfixppsfp[0] + i * gdat.numbpsfptotl + m * gdat.numbener * gdat.numbpsfptotl
                if gdat.strganglunit != None:
                    strganglunit = gdat.strganglunit
                else:
                    strganglunit = ''
                if gdat.psfntype == 'singgaus':
                    strg = r'$\sigma = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp], strganglunit)
                    # temp
                elif gdat.psfntype == 'singking':
                    strg = r'$\sigma = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp], strganglunit) + '\n'
                    strg += r'$\gamma = %.3g$' % gdatmodi.thissampvarb[indxsamptemp+1]
                elif gdat.psfntype == 'doubgaus':
                    strg = r'$f = %.3g$' % gdatmodi.thissampvarb[indxsamptemp] + '\n'
                    strg += r'$\sigma = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp+1], strganglunit) + '\n'
                    strg += r'$\sigma = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp+2], strganglunit)
                elif gdat.psfntype == 'gausking':
                    strg = r'$f_G = %.3g$' % gdatmodi.thissampvarb[indxsamptemp] + '\n'
                    strg += r'$\sigma_G = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp+1], strganglunit) + '\n'
                    strg += r'$\sigma_K = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp+2], strganglunit) + '\n'
                    strg += r'$\gamma = %.3g$' % gdatmodi.thissampvarb[indxsamptemp+3]
                elif gdat.psfntype == 'doubking':
                    strg = r'$f_c = %.3g$' % gdatmodi.thissampvarb[indxsamptemp] + '\n'
                    strg += r'$\sigma_c = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp+1], strganglunit) + '\n'
                    strg += r'$\gamma_c = %.3g$' % gdatmodi.thissampvarb[indxsamptemp+2] + '\n'
                    strg += r'$\sigma_t = %.3g$%s' % (gdat.anglfact * gdatmodi.thissampvarb[indxsamptemp+3], strganglunit) + '\n'
                    strg += r'$\gamma_t = %.3g$' % gdatmodi.thissampvarb[indxsamptemp+4]
                axis.text(0.2, 0.2, strg, va='center', ha='center', transform=axis.transAxes, fontsize=18)
            
    plt.tight_layout()
    path = retr_plotpath(gdat, 'psfn', gdatmodi)
    plt.savefig(path)
    plt.close(figr)
   

def plot_fwhm(gdat, gdatmodi):
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))

    tranfwhm = transpose(gdatmodi.thisfwhm)
    imag = plt.pcolor(gdat.enerfact * gdat.meanener, gdat.indxevtt, rad2deg(tranfwhm), cmap='BuPu')
    plt.colorbar(imag, ax=axis, fraction=0.05)
    axis.set_xscale('log')
    axis.set_ylabel('PSF Class')
    axis.set_xlabel(r'$E$ [%s]' % gdat.strgenerunit)
    axis.set_yticks(gdat.indxevtt + 0.5)
    axis.set_yticklabels(['%d' % m for m in gdat.evttfull[gdat.indxevttincl]])
    axis.set_xticks(gdat.binsener * gdat.enerfact)
    axis.set_xticklabels(['%.2g' % (gdat.binsener[i] * gdat.enerfact) for i in arange(gdat.numbener + 1)])
    axis.set_xlim([gdat.binsener[0] * gdat.enerfact, gdat.binsener[-1] * gdat.enerfact])
    for i in gdat.indxener:
        for m in gdat.indxevtt:
            axis.text(gdat.meanener[i], gdat.indxevttincl[m] + 0.5, r'$%.3g^\circ$' % rad2deg(tranfwhm[m, i]), ha='center', va='center', fontsize=14)

    plt.tight_layout()
    path = retr_plotpath(gdat, 'fwhm', gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    
    
def plot_datacntshist(gdat):

    figr, axgr = plt.subplots(gdat.numbevtt, gdat.numbener, figsize=(gdat.numbener * gdat.plotsize, gdat.numbevtt * gdat.plotsize))
    if gdat.numbevtt == 1:
        axgr = [axgr]
    for m, axrw in enumerate(axgr):
        if gdat.numbener == 1:
            axrw = [axrw]
        for i, axis in enumerate(axrw):
            
            datacntstemp = gdat.datacnts[i, :, m]
            
            maxmdatacntstemp = amax(datacntstemp)
            minmdatacntstemp = 0.
            gdat.binscntstemp = linspace(minmdatacntstemp, maxmdatacntstemp, 20)
            meancntstemp = (gdat.binscntstemp[1:] + gdat.binscntstemp[0:-1]) / 2.
            diffcntstemp = gdat.binscntstemp[1:] - gdat.binscntstemp[0:-1]
            
            datacntshist = axis.hist(datacntstemp, gdat.binscntstemp, color='b')[0]

            init = [meancntstemp[argmax(datacntshist)], 1.]
            
            axis.set_xlim([amin(gdat.binscntstemp), amax(gdat.binscntstemp)])
            if m == gdat.numbevtt - 1:
                axis.set_xlabel(r'$k$')
            if m == 0 and gdat.enerbins:
                axis.set_title(gdat.strgbinsener[i])
            if i == 0 and gdat.evttbins:
                axis.set_ylabel(gdat.strgevtt[m])
        
    plt.tight_layout()
    plt.savefig(gdat.pathinit + 'datacntshist.pdf')
    plt.close(figr)
    
    
def plot_intr():
    
    with plt.xkcd():

        from matplotlib import patheffects
        mpl.rcParams['path.effects'] = [patheffects.withStroke(linewidth=0)]

        figr, axis = plt.subplots(figsize=(2 * gdat.plotsize, gdat.plotsize))

        catl = arange(80)
        probcatl = pss.pmf(catl, 30.) + 0.5 * pss.pmf(catl, 60.)
        axis.plot(catl, probcatl)
        axis.set_xticks([10, 30, 60])
        axis.set_xticklabels(["Crackpot's Catalog", "Best-fit catalog", "Not-so-best-fit catalog"])
        axis.set_yticks([])
        text = axis.set_title("Exploring the catalog space with Probabilistic cataloging")
        text.set_position([.5, 1.05])
        axis.set_xlabel('Catalog index')
        axis.set_ylabel("Probability")
        
        axis.tick_params(axis='x', colors='#B6E954')
        axis.tick_params(axis='y', colors='#B6E954')
        axis.spines['bottom'].set_color('#B6E954')
        axis.spines['top'].set_color('#B6E954') 
        axis.spines['right'].set_color('#B6E954')
        axis.spines['left'].set_color('#B6E954')
        axis.yaxis.label.set_color('#B6E954')
        axis.xaxis.label.set_color('#B6E954')
        axis.title.set_color('#B6E954')

        axis.set_axis_bgcolor('black')
        figr.set_facecolor('black')
        plt.tight_layout()
        plt.savefig(os.environ["PCAT_DATA_PATH"] + '/imag/talkintr.pdf', facecolor=figr.get_facecolor())
        plt.close()  
        
        
def plot_eval(gdat):

    if gdat.truevarioaxi:
        psfntemp = copy(gdat.truepsfn[0, :, 0, 0])
    else:
        psfntemp = copy(gdat.truepsfn[0, :, 0])
    psfntemp /= amax(psfntemp)
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    for k in range(gdat.numbfluxprox + 1):
        if k == 0 or k == gdat.numbfluxprox:
            alph = 1.
            if k == 0:
                labl = 'Dimmest PS'
                colr = 'b'
            else:
                labl = 'Brightest PS'
                colr = 'g'
        else:
            alph = 0.2
            labl = None
            colr = 'black'
        axis.plot(gdat.binsanglplot, gdat.binsfluxprox[k] * psfntemp, label=labl, color=colr, alpha=alph)
        axis.set_xlim([amin(gdat.binsanglplot), amax(gdat.binsanglplot)])
        if k > 0:
            axis.axvline(gdat.anglfact * gdat.maxmangleval[k-1], ls='--', alpha=alph, color=colr)
    axis.set_yscale('log')
    axis.set_xlabel(r'$\theta$%s' % gdat.strganglunit)
    axis.set_ylabel('$%s$ [%s]' % (gdat.strgflux, gdat.strgfluxunit))

    limt = gdat.specfraceval * amax(gdat.binsfluxprox[0] * psfntemp)
    maxmangltemp = interp(1e-1 * limt, gdat.binsfluxprox[k] * psfntemp[::-1], gdat.binsanglplot[::-1])
    
    if limt > 0:
        axis.axhline(limt, color='red', ls=':', label='Flux floor')
    axis.set_xlim([None, maxmangltemp])
    axis.set_ylim([1e-3 * limt, None])
    legd = axis.legend(frameon=True, shadow=True, fancybox=True, framealpha=1.)
    legd.get_frame().set_facecolor('white')
    
    plt.tight_layout()
    plt.savefig(gdat.pathinit + 'eval.pdf')
    plt.close(figr)


def plot_mosa(gdat):

    # empty global object
    gdatmodi = tdpy.util.gdatstrt()
    
    # data structure to hold the indices of model PS to be compared to the reference catalog 
    gdatmodi.indxmodlpntscomp = [[] for l in gdat.indxpopl]
    
    numbrows = 3
    numbcols = 2
    numbsampmosa = numbrows * numbcols
    if numbsampmosa <= gdat.numbsamp:
        indxsampmosa = choice(gdat.indxsamp, size=numbsampmosa, replace=False)
        for l in gdat.indxpopl:
            for i in gdat.indxener:
                for m in gdat.indxevttplot:
                    figr, axgr = plt.subplots(numbrows, numbcols, figsize=(numbcols * gdat.plotsize, numbrows * gdat.plotsize))
                    for a, axrw in enumerate(axgr):
                        for b, axis in enumerate(axrw):
                            
                            gdatmodi.thissampvarb = gdat.listsampvarb[indxsampmosa[numbcols*a+b], :].flatten()
                            if gdat.numbtrap > 0:
                                gdatmodi.thisindxsamplgal, gdatmodi.thisindxsampbgal, gdatmodi.thisindxsampspec, \
                                                                gdatmodi.thisindxsampspep, gdatmodi.thisindxsampcomp = retr_indx(gdat, gdat.listindxpntsfull[l])
                                gdatmodi.indxmodlpntscomp[l] = retr_indxpntscomp(gdat, gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l]], \
                                                                                                                gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l]])
                                # cross-correlate with the reference catalog
                                if gdat.trueinfo:
                                    gdatmodi.trueindxpntsassc = []
                                    indxmodl, trueindxpntsassc = corr_catl(gdat, l, gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l]], \
                                                                                                                        gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l]], \
                                                                                                                        gdatmodi.thissampvarb[gdatmodi.thisindxsampspec[l]])
                                    gdatmodi.trueindxpntsassc.append(trueindxpntsassc)
         
                            if a == numbrows - 1:
                                axis.set_xlabel(gdat.strgxaxitotl)
                            else:
                                axis.set_xticklabels([])
                            if b == 0:
                                axis.set_ylabel(gdat.strgyaxi)
                            else:
                                axis.set_yticklabels([])
                            
                            imag = retr_imag(gdat, axis, gdat.datacnts, i, m, vmin=gdat.minmdatacnts[i], vmax=gdat.maxmdatacnts[i], scal=gdat.scalmaps)
                            supr_fram(gdat, gdatmodi, axis, i, l)
                    
                    if gdat.enerbins:
                        plt.figtext(0.5, 0.93, gdat.strgbinsener[i], ha='center', va='center')
                    axiscomm = figr.add_axes([0.92, 0.1, 0.02, 0.8])
                    cbar = figr.colorbar(imag, cax=axiscomm)
                    cbar.set_ticks(gdat.tickdatacnts[i, :])
                    cbar.set_ticklabels(gdat.labldatacnts[i, :])
                    plt.subplots_adjust(left=0.1, top=.91, hspace=0.01, wspace=0.05, bottom=0.09)
                    if l == 1:
                        strg = ''
                    else:
                        strg = '_pop%d' % l
                    if m == None:
                        path = gdat.pathpost + 'mosa' + strg + '_%dA.pdf' % (gdat.indxenerincl[i])
                    else:
                        path = gdat.pathpost + 'mosa' + strg + '_%d%d.pdf' % (gdat.indxenerincl[i], gdat.indxevttincl[m])
                    plt.savefig(path)
                    plt.close(figr)
    else:
        if gdat.verbtype > 0:
            print 'Skipping the mosaic image plot...'


def plot_grap(plottype='igal', verbtype=0):
        
    figr, axis = plt.subplots(figsize=(6, 6))

    grap = nx.DiGraph()
    if plottype == 'igal':
        listcolr = ['black', 'olive', 'black', 'black', 'black', 'olive', 'olive', 'olive', 'olive', 'black', 'olive', 'olive', \
                                                                            'magenta', 'magenta', 'magenta', 'magenta', 'magenta', 'black']
    if plottype == 'ngal':
        listcolr = ['black', 'olive', 'black', 'olive', 'olive', 'olive', 'black', 'olive', 'olive', 'magenta', 'magenta', 'magenta', 'magenta', 'black']

    grap.add_edges_from([ \
                         ('fluxdistslop', 'flux'), \
                         ('sinddistslop', 'sind'), \
                         ('meanpnts', 'numbpnts'), \
                         ('modl','data'), \
                         ('psfp', 'modl'), \
                         ('bacp', 'modl'), \
                         ('lgal','modl'), \
                         ('bgal','modl'), \
                         ('flux','modl'), \
                         ('sind','modl'), \
                         ('numbpnts','lgal'), \
                         ('numbpnts','bgal'), \
                         ('numbpnts','flux'), \
                         ('numbpnts', 'sind') \
                        ])
    
    if plottype == 'igal':
        grap.add_edges_from([ \
                             ('numbpnts', 'expo'), \
                             ('expo', 'modl'), \
                             ('spatdistslop', 'lgal'), \
                             ('spatdistslop', 'bgal') \
                            ])
    if plottype == 'ngal' or plottype == 'lens':
        pass

        
    labl = {}
    labl['numbpnts'] = '$N$'
    labl['meanpnts'] = r'$\mu$'
    if plottype == 'igal':
        labl['fluxdistslop'] = r'$\vec{\alpha}$'
        labl['sinddistslop'] = r'$\vec{\beta}$'
        labl['spatdistslop'] = r'$\vec{\gamma}$'
    if plottype == 'ngal':
        labl['fluxdistslop'] = r'$\alpha$'
        labl['sinddistslop'] = r'$\beta$'
    labl['psfp'] = r'$\vec{\eta}$'
    labl['bacp'] = r'$\vec{A}$'
    labl['lgal'] = r'$\vec{l}$'
    labl['bgal'] = r'$\vec{b}$'
    labl['flux'] = r'$\vec{f}$'
    labl['sind'] = r'$\vec{s}$'
    if plottype == 'igal':
        labl['expo'] = r'$\vec{E_c}$'
    labl['modl'] = r'$\mathcal{M}$'
    labl['data'] = r'$\mathcal{D}$'
    
    posi = nx.circular_layout(grap)
    posi['numbpnts'] = array([0., 0.075])
    posi['meanpnts'] = array([0., 0.15])
    if plottype == 'igal':
        posi['spatdistslop'] = array([-0.2, 0.15])
    posi['fluxdistslop'] = array([0.2, 0.15])
    posi['sinddistslop'] = array([0.4, 0.15])
    if plottype == 'igal':
        posi['psfp'] = array([0.9, -0.0])
        posi['bacp'] = array([0.7, -0.0])
    if plottype == 'ngal':
        posi['psfp'] = array([0.7, -0.0])
        posi['bacp'] = array([0.5, -0.0])
    posi['lgal'] = array([-0.3, -0.0])
    posi['bgal'] = array([-0.1, -0.0])
    posi['flux'] = array([0.1, -0.0])
    posi['sind'] = array([0.3, -0.0])
    if plottype == 'igal':
        posi['expo'] = array([0.5, -0.0])
    posi['modl'] = array([0., -0.075])
    posi['data'] = array([0., -0.15])
   
    if verbtype > 0:
        print 'len(labl)'
        print len(labl) 
        print 'len(posi)'
        print len(posi)
        print 'grap.edges()'
        print grap.edges()
        print 'len(grap.edges())'
        print len(grap.edges())
        print 'len(listcolr)'
        print len(listcolr)

    size = 500
    nx.draw(grap, posi, labels=labl, ax=axis, edgelist=[], nodelist=[])
    nx.draw_networkx_edges(grap, posi, ax=axis, labels=labl, edge_color=listcolr)
    nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['modl', 'data'], node_color='grey', node_size=size)
    nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['numbpnts'], node_color='b', node_size=size)
    if plottype == 'igal':
        nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['meanpnts', 'spatdistslop', 'fluxdistslop', 'sinddistslop'], node_color='r', node_size=size)
        nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['lgal', 'bgal', 'flux', 'sind', 'expo'], node_color='g', node_size=size)
    if plottype == 'ngal':
        nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['meanpnts', 'fluxdistslop', 'sinddistslop'], node_color='r', node_size=size)
        nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['lgal', 'bgal', 'flux', 'sind'], node_color='g', node_size=size)
    nx.draw_networkx_nodes(grap, posi, ax=axis, labels=labl, nodelist=['psfp', 'bacp'], node_color='y', node_size=size)
    
    pathplot = os.environ["PCAT_DATA_PATH"] + '/imag/'
    plt.tight_layout()
    plt.savefig(pathplot + 'grap%s.pdf' % plottype)
    plt.close(figr)


def plot_3fgl_thrs(gdat):

    path = os.environ["PCAT_DATA_PATH"] + '/detthresh_P7v15source_4years_PL22.fits'
    fluxthrs = pf.getdata(path, 0)

    bgalfgl3 = linspace(-90., 90., 481)
    lgalfgl3 = linspace(-180., 180., 960)

    bgalexpo = linspace(-90., 90., 400)
    lgalexpo = linspace(-180., 180., 800)

    #fluxthrs = interp2d(lgalfgl3, bgalfgl3, fluxthrs)(lgalexpo, bgalexpo)
    fluxthrs = griddata([lgalfgl3, bgalfgl3], fluxthrs, [gdat.lgalheal])

    cntsthrs = fluxthrs * gdat.expo

    jbgal = where(abs(bgalexpo) < 10.)[0]
    jlgal = where(abs(lgalexpo) < 10.)[0]
    extent = [-10, 10, -10, 10]
    
    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    axis.set_xlabel(gdat.strgxaxitotl)
    axis.set_ylabel(gdat.strgyaxitotl)

    imag = plt.imshow(fluxthrs[amin(jbgal):amax(jbgal)+1, amin(jlghprofi):amax(jlghprofi)+1], origin='lower', cmap='Reds', extent=gdat.exttrofi)
    plt.colorbar(imag, fraction=0.05)
    plt.tight_layout()
    plt.savefig(gdat.pathplot + 'thrs.pdf')
    plt.close(figr)
    

def make_anim(gdat):

    listname = ['psfnprof', 'compfrac', 'compfracspec', 'scatpixl']
    listname += ['histspec', 'histflux', 'scatfluxsind', 'histfluxsind', 'histcnts', 'histsind', 'scatspec']
    listname += ['datacnts', 'resicnts', 'modlcnts', 'defl', 'convpsecodim', 'conv', 'convpsec']
    listname += ['factoaxi', 'errr', 'errrcnts']

    gdat.pathanim = gdat.pathplot + 'anim/'

    os.system('mkdir -p %s' % gdat.pathanim)
    if gdat.verbtype > 0:
        print 'Making animations...'
    for name in listname:
        
        strgswep = '%s*_swep*.pdf' % name
        listfile = fnmatch.filter(os.listdir(gdat.pathfram), strgswep)
        numbfile = len(listfile)
        liststrgextn = []
        for k in range(numbfile):
            liststrgextn.append((listfile[k].split(name)[1]).split('_')[0])
        
        liststrgextn = list(set(liststrgextn))
        
        for k in range(len(liststrgextn)):
    
            listfile = fnmatch.filter(os.listdir(gdat.pathfram), name + liststrgextn[k] + '_swep*.pdf')
            numbfile = len(listfile)
            
            indxfilelowr = int(ceil(numbfile * float(gdat.numbburn) / gdat.numbswep))
            if indxfilelowr < numbfile:
                indxfileanim = arange(indxfilelowr, numbfile)
            else:
                indxfileanim = array([])
          
            if indxfileanim.size == 0:
                if gdat.verbtype > 0:
                    print 'Skipping animation for %s...' % name
                continue
            else:
                if gdat.verbtype > 0:
                    print 'Producing animation for %s...' % name
                
            indxfileanim = choice(indxfileanim, replace=False, size=indxfileanim.size)
   
            cmnd = 'convert -delay 20 -density 300 -quality 100 '
            for n in range(indxfileanim.size):
                cmnd += '%s%s ' % (gdat.pathfram, listfile[indxfileanim[n]])
            cmnd += ' %s%s.gif' % (gdat.pathanim, name + liststrgextn[k])
            os.system(cmnd)

       
def plot_opti(gdat, gdatmodi):

    for k in gdat.indxswepopti:
        
        figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
            
        gdat.binsaccprati = logspace(-1., 1., 100)
        axis.hist(gdatmodi.propeffi, bins=gdat.binsaccprati)
        axis.set_ylim([0., gdat.numbstdp])
        axis.set_xlabel('$N_{acc}/N_{tot}$')
        axis.set_ylabel(r'N_{prop})')
        axis.legend(loc=2)
        plt.tight_layout()
        path = '%sopti_%d.pdf' % (gdat.pathinit, k)
        plt.savefig(path)
        plt.close(figr)

    os.system('convert -delay 10 %sopti*.pdf %s/opti.gif' % (gdat.pathinit, gdat.pathinit))


def plot_factoaxi(gdat, i, m, gdatmodi):

    figr, axis = plt.subplots(figsize=(gdat.plotsize, gdat.plotsize))
    if gdat.varioaxi:
        if gdatmodi == None:
            psfpoaxinorm = gdat.postpsfpoaxinorm
            psfpoaxiindx = gdat.postpsfpoaxiindx
        else:
            psfpoaxinorm = gdatmodi.thissampvarb[gdat.indxfixppsfpoaxinorm]
            psfpoaxiindx = gdatmodi.thissampvarb[gdat.indxfixppsfpoaxiindx]
        factoaxi = retr_factoaxi(gdat, gdat.binsoaxi, psfpoaxinorm, psfpoaxiindx)
        axis.plot(gdat.binsoaxi * gdat.anglfact, factoaxi[i, :], label='Sample', color='b')
    
    if gdat.truefactoaxi != None:
        axis.plot(gdat.binsoaxi * gdat.anglfact, gdat.truefactoaxi[i, :], label=gdat.truelabl, color='g', ls='--')
        axis.set_ylim([0., 2. * amax(gdat.truefactoaxi[i, :])])
    axis.set_xlabel(r'$\phi$%s' % gdat.strganglunit)
    axis.set_ylabel(r'f($\phi$)')
    axis.legend(loc=2)
    
    plt.tight_layout()
    path = retr_plotpath(gdat, 'factoaxi_%d%d' % (i, m), gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    

def plot_histcnts(gdat, l, gdatmodi):

    figr, axgr = plt.subplots(gdat.numbevtt, gdat.numbener, figsize=(gdat.numbener * gdat.plotsize, gdat.numbevtt * gdat.plotsize))
    if gdat.numbevtt == 1:
        axgr = [axgr]
    for m, axrw in enumerate(axgr):
        if gdat.numbener == 1:
            axrw = [axrw]
        for i, axis in enumerate(axrw):
    
            xdat = gdat.meancnts[i, :]
            if gdatmodi == None:
                ydat = gdat.medicntshist[l][i, :]
                yerr = gdat.errrcntshist[l][:, i, :]
                axis.errorbar(xdat, ydat, ls='', yerr=yerr, lw=1, marker='o', markersize=5, color='black')
            else:
                axis.hist(gdatmodi.thiscnts[l][i, :, m], gdat.binscnts[i, :], alpha=gdat.alphmrkr, color='b', log=True, label='Sample')
            
            if gdat.trueinfo:
                try:
                    truehist = axis.hist(gdat.truecnts[l][i, :, m], gdat.binscnts[i, :], alpha=gdat.alphmrkr, color='g', log=True, label=gdat.truelabl)
                except:
                    if gdat.verbtype > 0:
                        print 'Skipping PS count histogram plot...'
                if gdat.datatype == 'mock' and gdat.exprinfo:
                    axis.hist(gdat.exprcnts[i, :, m], gdat.binscnts[i, :], alpha=gdat.alphmrkr, color='red', log=True, label=gdat.strgcatl)
            if m == gdat.numbevtt - 1:
                axis.set_xlabel(r'$k$')
            axis.set_xscale('log')
            axis.set_ylim(gdat.limshist)
            if m == 0 and gdat.enerbins:
                axis.set_title(gdat.strgbinsener[i])
            if i == 0 and gdat.evttbins:
                axis.set_ylabel(gdat.strgevtt[m])
            if m == gdat.numbevtt / 2 and i == gdat.numbener / 2:
                axis.legend()
        
    plt.tight_layout()
    path = retr_plotpath(gdat, 'histcnts_pop%d' % l, gdatmodi)
    plt.savefig(path)
    plt.close(figr)
    

def plot_defl(gdat, gdatmodi, defl=None, indxdefl=None):

    if defl != None and gdatmodi != None:
        strg = 'defl%d' % indxdefl
        pathfold = gdat.pathfram
    elif gdatmodi != None:
        defl = gdatmodi.thisdefl
        strg = 'defl'
        pathfold = gdat.pathfram
    else:
        defl = gdat.mockdefl
        strg = 'mockdefl'
        pathfold = gdat.pathinit

    figr, axis, path = init_figr(gdat, strg, gdatmodi, indxpoplplot=0, pathfold=pathfold)
    make_catllabl(gdat, axis)
    draw_frambndr(gdat, axis)
  
    defllgal = defl[:, :, 0]
    deflbgal = defl[:, :, 1]
    fact = 10
    deflmagn = sqrt(defllgal[::fact, ::fact]**2 + deflbgal[::fact, ::fact]**2)
    ptch = axis.quiver(gdat.anglfact * gdat.lgalgridcart[::fact, ::fact], gdat.anglfact * gdat.bgalgridcart[::fact, ::fact], \
                                                 gdat.fluxfactplot * defllgal[::fact, ::fact], gdat.fluxfactplot * deflbgal[::fact, ::fact], units='xy')
  
    if gdatmodi != None:
        supr_fram(gdat, gdatmodi, axis, 0, 0)
    #plt.subplots_adjust(left=0.2, bottom=0.15, top=0.75, right=0.85)
    plt.savefig(path)
    plt.close(figr)
    
    
def plot_datacnts(gdat, indxpoplplot, gdatmodi, indxenerplot, indxevttplot):

    figr, axis, path = init_figr(gdat, 'datacnts', gdatmodi, indxenerplot, indxevttplot, indxpoplplot)
    make_catllabl(gdat, axis)
    if gdat.correxpo:
        imag = retr_imag(gdat, axis, gdat.datacnts, indxenerplot, indxevttplot, vmin=gdat.minmdatacnts[indxenerplot], vmax=gdat.maxmdatacnts[indxenerplot], scal=gdat.scalmaps)
        make_cbar(gdat, axis, imag, indxenerplot, tick=gdat.tickdatacnts[indxenerplot, :], labl=gdat.labldatacnts[indxenerplot, :])
    else:
        imag = retr_scat(gdat, axis, gdat.datacnts, indxenerplot, indxevttplot)
    supr_fram(gdat, gdatmodi, axis, indxenerplot, indxpoplplot)
    plt.tight_layout()
    plt.savefig(path)
    plt.close(figr)
    
    
def plot_genemaps(gdat, strg, gdatmodi):
    
    figr, axis, path = init_figr(gdat, strg, gdatmodi)
    if gdatmodi == None:
        maps = getattr(gdat, 'medi' + strg)
    else:
        maps = getattr(gdatmodi, 'this' + strg)
    
    # temp
    maps = maps.flatten()[None, :, None]

    imag = retr_imag(gdat, axis, maps, cmap='Purples')
    make_cbar(gdat, axis, imag)

    plt.tight_layout()
    plt.savefig(path)
    plt.close(figr)
    

def plot_modlcnts(gdat, indxpoplplot, gdatmodi, indxenerplot, indxevttplot):

    figr, axis, path = init_figr(gdat, 'modlcnts', gdatmodi, indxenerplot, indxevttplot, indxpoplplot)
    make_catllabl(gdat, axis)
    if gdatmodi != None:
        if gdat.pixltype == 'unbd':
            modltemp = gdatmodi.thismodlflux
        else:
            modltemp = gdatmodi.thismodlcnts
    else:
        modltemp = gdat.medimodlcnts
    imag = retr_imag(gdat, axis, modltemp, indxenerplot, indxevttplot, vmin=gdat.minmdatacnts[indxenerplot], \
                                                                                                                vmax=gdat.maxmdatacnts[indxenerplot], scal=gdat.scalmaps)
    make_cbar(gdat, axis, imag, indxenerplot, tick=gdat.tickdatacnts[indxenerplot, :], labl=gdat.labldatacnts[indxenerplot, :])
    if gdatmodi != None:
        supr_fram(gdat, gdatmodi, axis, indxenerplot, indxpoplplot)
    plt.tight_layout()
    plt.savefig(path)
    plt.close(figr)
    
    
def plot_resicnts(gdat, indxpoplplot, gdatmodi, indxenerplot, indxevttplot):

    figr, axis, path = init_figr(gdat, 'resicnts', gdatmodi, indxenerplot, indxevttplot, indxpoplplot)
    make_catllabl(gdat, axis)
    if gdatmodi != None:
        resitemp = gdatmodi.thisresicnts
    else:
        resitemp = gdat.medimodlcnts
        
    imag = retr_imag(gdat, axis, resitemp, indxenerplot, indxevttplot, vmax=gdat.maxmresicnts[indxenerplot], cmap='RdBu', scal=gdat.scalmaps)
    if gdatmodi != None:
        supr_fram(gdat, gdatmodi, axis, indxenerplot, indxpoplplot)
    make_cbar(gdat, axis, imag, indxenerplot, tick=gdat.tickresicnts[indxenerplot, :], labl=gdat.lablresicnts[indxenerplot, :])
    plt.tight_layout()
    plt.savefig(path)
    plt.close(figr)
    
    
def plot_errrcnts(gdat, gdatmodi, indxenerplot, indxevttplot):
   
    listtupl = [ \
                #['errrcnts', False, gdatmodi.thiserrrcnts, gdat.maxmerrrcnts[indxenerplot], gdat.tickerrrcnts[indxenerplot, :], gdat.lablerrrcnts[indxenerplot, :]], \
                #[    'errr',  True,     gdatmodi.thiserrr,     gdat.maxmerrr[indxenerplot],     gdat.tickerrr[indxenerplot, :],     gdat.lablerrr[indxenerplot, :]], \
                ['errrcnts', False, gdatmodi.thiserrrcnts, None, None, None], \
                [    'errr',  True,     gdatmodi.thiserrr, None, None, None], \
               ]
    numbiter = len(listtupl)
    for k in range(numbiter):
        strg, boolmean, varb, vmax, tick, labl = listtupl[k] 
        figr, axis, path = init_figr(gdat, strg, gdatmodi, indxenerplot, indxevttplot)
        imag = retr_imag(gdat, axis, varb, indxenerplot, indxevttplot, vmax=vmax, cmap='RdBu', mean=boolmean)
        make_cbar(gdat, axis, imag, indxenerplot, tick=tick, labl=labl)
        plt.tight_layout()
        plt.savefig(path)
        plt.close(figr)
    
    
def plot_catlfram(gdat, gdatmodi, indxpoplplot, indxenerplot, indxevttplot):
    
    figr, axis, path = init_figr(gdat, 'catlfram', gdatmodi, indxenerplot, indxevttplot, indxpoplplot)
    make_catllabl(gdat, axis)

    if False:
        offs = 0.05 * gdat.maxmgang
        if gdat.trueinfo:
            for l in gdat.indxpopl:
                numbpnts = int(gdat.truefixp[gdat.indxfixpnumbpnts[l]])
                for a in range(numbpnts):
                    if gdat.correxpo:
                        cnts = copy(gdat.truecnts[l][indxenerplot, a, :])
                        if indxevttplot == None:
                            cnts = sum(cnts)
                        else:
                            cnts = cnts[indxevttplot]
                    else:
                        cnts = copy(gdat.truespec[l][0, indxenerplot, a])
                    axis.text(gdat.anglfact * (gdat.truelgal[l][a] + offs), gdat.anglfact * (gdat.truebgal[l][a] - offs), '%d' % cnts, color='g', fontsize=13)
        
        for l in gdat.indxpopl:
            numbpnts = int(gdatmodi.thissampvarb[gdat.indxfixpnumbpnts[l]])
            for a in range(numbpnts):
                if gdat.correxpo:
                    cnts = copy(gdatmodi.thiscnts[l][indxenerplot, a, :])
                    if indxevttplot == None:
                        cnts = sum(cnts)
                    else:
                        cnts = cnts[indxevttplot]
                else:
                    cnts = copy(gdatmodi.thisspec[l][indxenerplot, a])
                axis.text(gdat.anglfact * (gdatmodi.thissampvarb[gdatmodi.thisindxsamplgal[l][a]] - offs), \
                                        gdat.anglfact * (gdatmodi.thissampvarb[gdatmodi.thisindxsampbgal[l][a]] + offs), '%d' % cnts, color='b', fontsize=13)
        
        if indxevttplot == None:
            plt.figtext(0.76, 0.92, '$C_{back} = %d$' % mean(gdatmodi.thisbackcntsmean[indxenerplot, :]), fontsize=18)
        else:
            plt.figtext(0.76, 0.92, '$C_{back} = %d$' % gdatmodi.thisbackcntsmean[indxenerplot, indxevttplot], fontsize=18)
        
    plt.tight_layout()
    plt.savefig(path)
    plt.close(figr)

    
def plot_pntsdiff():

    tempindxpntsfull = []
    tempnumbpnts = 10
    tempindxpntsfull.append(range(tempnumbpnts))
    tempsamp = rand(gdat.numbpara)
    tempsamp[gdat.indxfixpnumbpnts] = array([tempnumbpnts])
    tempsamp[gdat.indxfixpmeanpnts] = cdfn_logt(array([tempnumbpnts]), minmmeanpnts, factmeanpnts)
    tempsamp[gdat.indxfixpfluxdistslop] = cdfn_atan(array([1.5]), minmfluxdistslop, factfluxdistslop)
    tempsamp[gdat.indxfixppsfp] = 0.5
    for c in gdat.indxback:
        tempsamp[gdat.indxfixpbacp[c, 0]] = cdfn_logt(array([1.]), minmbacp[c], factbacp[c])
    
    tempsampvarb = retr_sampvarb(gdat, gdatmodi.thisindxpntsfull, drmcsamp[:, 0])
    temppntsflux, temppntscnts, tempmodlflux, tempmodlcnts = retr_maps(gdat, tempindxpntsfull, tempsampvarb)

    pntscnts = tempcnts[0, :, 0] * gdat.expo[0, :, 0] * gdat.apix * gdat.diffener[0]
    isotcnts = isotflux[0, :, 0] * gdat.expo[0, :, 0] * gdat.apix * gdat.diffener[0]
    
    totlcnts0 = isotcnts
    totlcnts1 = pntscnts / 1e6 + isotcnts
    
    nrept = 100
    totlcntsheal0 = zeros((nrept, gdat.numbpixlheal))
    totlcntsheal1 = zeros((nrept, gdat.numbpixlheal))
    for k in range(nrept):
        for n in range(gdat.indxpixlrofi.size):
            totlcntsheal0[k, gdat.indxpixlrofi[n]] = poisson(totlcnts0[n])
            totlcntsheal1[k, gdat.indxpixlrofi[n]] = poisson(totlcnts1[n])
          
    maxmcnts = max(amax(totlcntsheal0), amax(totlcntsheal1))
    gdat.binscnts = linspace(0., maxmcnts, maxmcnts + 2)
    diffcnts = gdat.binscnts[1:] - gdat.binscnts[:-1]
    meancnts = (gdat.binscnts[1:] + gdat.binscnts[:-1]) / 2.
    
    hist0 = empty((nrept, maxmcnts + 1))
    hist1 = empty((nrept, maxmcnts + 1))
    for k in range(nrept):
        hist0[k, :] = histogram(totlcntsheal0[k, gdat.indxpixlrofi], gdat.binscnts)[0].astype(float)
        hist0[k, :] *= 1. / sum(hist0[k, :]) / diffcnts
        hist1[k, :] = histogram(totlcntsheal1[k, gdat.indxpixlrofi], gdat.binscnts)[0].astype(float)
        hist1[k, :] *= 1. / sum(hist1[k, :]) / diffcnts
        
    
    totlcntscart0 = tdpy.util.retr_cart(totlcntsheal0[0, :], minmlgal=gdat.anglfact*gdat.minmlgal, maxmlgal=gdat.anglfact*gdat.maxmlgal, \
                                                                                            minmbgal=gdat.anglfact*gdat.minmbgal, maxmbgal=gdat.anglfact*gdat.maxmbgal)
    totlcntscart1 = tdpy.util.retr_cart(totlcntsheal1[0, :], minmlgal=gdat.anglfact*gdat.minmlgal, maxmlgal=gdat.anglfact*gdat.maxmlgal, \
                                                                                            minmbgal=gdat.anglfact*gdat.minmbgal, maxmbgal=gdat.anglfact*gdat.maxmbgal)
    
    fig = plt.figure(figsize=(2 * gdat.plotsize, 2 * gdat.plotsize))
    axis = figr.add_subplot(221)
    imag = axis.imshow(totlcntscart0, origin='lower', cmap='Reds', extent=gdat.exttrofi)
    plt.colorbar(imag, ax=axis, fraction=0.05)
    
    axis.set_xlabel(gdat.strgxaxitotl)
    axis.set_ylabel(gdat.strgyaxitotl)
    if gdat.exprtype == 'ferm':
        axis.set_xlim([gdat.maxmlgal, gdat.minmlgal])
        axis.set_ylim([gdat.minmbgal, gdat.maxmbgal])
    else:
        axis.set_xlim(array([gdat.maxmlgal, gdat.minmlgal]) * 3600.)
        axis.set_ylim(array([gdat.minmbgal, gdat.maxmbgal]) * 3600.)
    
    axis.set_title('Isotropic')
    
    axis = figr.add_subplot(222)
    imag = axis.imshow(totlcntscart1, origin='lower', cmap='Reds', extent=gdat.exttrofi)
    plt.colorbar(imag, ax=axis, fraction=0.05)

    axis.set_xlabel(r'$x$ [$^\circ$]')
    axis.set_xlim([gdat.maxmlgal, gdat.minmlgal])
    axis.set_ylim([gdat.minmbgal, gdat.maxmbgal])
    axis.set_title('Isotropic + Unresolved PS')
    
    axis.scatter(tempsampvarb[trueindxsamplgal], tempsampvarb[trueindxsampbgal], s=50, alpha=gdat.alphmrkr, marker='x', color='g', linewidth=2)
    
    axis = figr.add_subplot(212)

    tdpy.mcmc.plot_braz(ax, meancnts, hist0,  lcol='lightgreen', alpha=gdat.alphmrkr, dcol='green', mcol='darkgreen', labl='Isotropic')
    tdpy.mcmc.plot_braz(ax, meancnts, hist1, lcol='lightblue', alpha=gdat.alphmrkr, dcol='blue', mcol='darkblue', labl='Isotropic + Unresolved PS')

    axis.set_xlabel('$k$')
    axis.set_ylabel('d$P$/d$k$')
    axis.set_yscale('log')
    axis.legend()

    plt.tight_layout()
    plt.savefig(gdat.pathplot + 'pntsdiff.pdf')
    plt.close(figr)
    
