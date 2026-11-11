---
title: "Subcortical Electrophysiology Mapping (SEM)"
date: "2017-04-08T21:01:20"
lastmod: "2022-03-16T14:34:53"
weight: 2
---

Subcortical Electrophysiology Mapping is a technique that pools data recorded from DBS electrodes across patients and maps this data onto anatomical space.

![Methods summary in four panels: images in standard space, electrode localization, recordings per contact, interpolated map](fig_1.png)

*Methods summary. Postoperative images are transformed to standard space (A); electrodes are localized for each patient (B); electrophysiological recording estimates (such as beta power) are projected onto the midpoint of each contact pair (C); This leads to a 3D point cloud, each point associated with a beta power value. These points are used to fit a scattered interpolant to define beta values within covered subcortical space (D).*

The methodology was successfully applied for the first time on beta-power recorded within the subthalamic nucleus in the two papers listed below.

> [Horn, A., Neumann, W.-J., Degen, K., Schneider, G.-H., & Kühn, A. A. (2017). Toward an electrophysiological “sweet spot” for deep brain stimulation in the subthalamic nucleus. *Human Brain Mapping*, *35*(3), 5083–14.](https://doi.org/10.1002/hbm.23594)
>
> [Accolla, E. A., Horn, A., Herrojo Ruiz, M., Neumann, W.-J., & Kühn, A. A. (2017). Reply: Oscillatory coupling of the subthalamic nucleus in obsessive compulsive disorder. *Brain : a Journal of Neurology*, *140*(9), e57–e57.](https://doi.org/10.1093/brain/awx165)

Main findings of this paper were reproduced and extended by the following two studies of different labs:

> [van Wijk BCM, Pogosyan A, Hariz MI, Akram H, Foltynie T, Limousin P, Horn A, Ewert S, Brown P, Litvak V (2017). Localization of beta and high-frequency oscillations within the subthalamic nucleus region. NeuroImage: Clinical.](https://www.ncbi.nlm.nih.gov/pubmed/28794978)

> [Geng, X., Xu, X., Horn, A., Li, N., Ling, Z., Brown, P., & Wang, S. (2018). Intra-operative characterisation of subthalamic oscillations in Parkinson’s disease. *Clinical Neurophysiology*, *0*(0).](https://www.clinph-journal.com/article/S1388-2457(18)30105-6/fulltext)

Similarly, the method was applied to theta oscillations in the internal part of the pallidum in the following publication:

> [Neumann, W.-J., Horn, A., Ewert, S., Huebl, J., Brücke, C., Slentz, C., et al. (2017). A localized pallidal physiomarker in cervical dystonia. *Annals of Neurology*.](https://doi.org/10.1002/ana.25095)

Finally, the concept was extended to electrophysiological features recorded during movement in this study:

> [Lofredi, R., Neumann, W.-J., Bock, A., Horn, A., Huebl, J., Siegert, S., et al. (2018). Dopamine-dependent scaling of subthalamic gamma bursts with movement velocity in patients with Parkinson’s disease. eLife, 7, e31895.](https://elifesciences.org/articles/31895)

The methodology is implemented in the *Lead Group* module supplied within Lead-DBS. The technique was summarized using the example of the same publication in [our blog post here](/subcortical-electrophysiology-mapping/).

{{< button href="/subcortical-electrophysiology-mapping/" >}}Read our blog post explaining SEM in detail here{{< /button >}}

In theory, this mapping technique could be applied to virtually any measure that is prevalent for each patient, each DBS electrode, each DBS electrode contact or each DBS electrode contact pair. For instance, behavioral measures, electrophysiological recordings / task signatures, clinical outcome measures, patient demographical information, surgical techniques / treating DBS centers could be mapped to the subcortex using DBS electrode reconstructions from multiple patients.

For instance, a similar approach has been used to map *clinical outcome* (instead of electrophysiological measures) to the subcortex in these following (and other) studies. Some of the studies convolved DBS stimulation location by modeling a volume of activated tissue (VTA):

> [Butson, C. R., Cooper, S. E., Henderson, J. M., Wolgamuth, B., & McIntyre, C. C. (2011). Probabilistic analysis of activation volumes generated during deep brain stimulation., *54*(3), 2096–2104.](https://doi.org/10.1016/j.neuroimage.2010.10.059)
>
> [Schönecker, T., Gruber, D., Kivi, A., Müller, B., Lobsien, E., Schneider, G.-H., et al. (2015). Postoperative MRI localisation of electrodes and clinical efficacy of pallidal deep brain stimulation in cervical dystonia. *Journal of Neurology, Neurosurgery, and Psychiatry*, *86*(8), 833–839.](https://doi.org/10.1136/jnnp-2014-308159)
>
> [Maks, C. B., Butson, C. R., Walter, B. L., Vitek, J. L., & McIntyre, C. C. (2009). Deep brain stimulation activation volumes and their association with neurophysiological mapping and therapeutic outcomes. *Journal of Neurology, Neurosurgery, and Psychiatry*, *80*(6), 659–666.](https://doi.org/10.1136/jnnp.2007.126219)
>
> [Nowinski, W. L., Belov, D., Pollak, P., & Benabid, A.-L. (2005). Statistical analysis of 168 bilateral subthalamic nucleus implantations by means of the probabilistic functional atlas. *Neurosurgery*, *57*(4 Suppl), 319–30– discussion 319–30.](https://www.ncbi.nlm.nih.gov/pubmed/16234681)
>
> [Garcia-Garcia, D., Guridi, J., Toledo, J. B., Alegre, M., Obeso, J. A., & Rodríguez-Oroz, M. C. (2016). Stimulation sites in the subthalamic nucleus and clinical improvement in Parkinson’s disease: a new approach for active contact localization. *Journal of Neurosurgery*, 1–12.](https://www.ncbi.nlm.nih.gov/pubmed/26848922)
>
> [Welter, M.-L., Schüpbach, M., Czernecki, V., Karachi, C., Fernandez-Vidal, S., Golmard, J.-L., et al. (2014). Optimal target localization for subthalamic stimulation in patients with Parkinson disease. *Neurology*, *82*(15), 1352–1361.](https://doi.org/10.1212/WNL.0000000000000315)
>
> [Eisenstein, S. A., Koller, J. M., Black, K. D., Campbell, M. C., Lugar, H. M., Ushe, M., et al. (2014). Functional anatomy of subthalamic nucleus stimulation in Parkinson disease. *Annals of Neurology*, *76*(2), 279–295.](https://doi.org/10.1002/ana.24204)
