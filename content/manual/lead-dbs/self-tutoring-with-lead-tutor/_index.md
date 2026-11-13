---
{
  "title": "Self-Tutoring with Lead-Tutor",
  "linkTitle": "Lead Tutor",
  "layout": "manual",
  "weight": 5,
  "manual_group": "lead-dbs",
  "description": "Practice the Lead-DBS workflow with Lead-Tutor.",
  "source_url": "https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor",
  "manual_title": "Self-Tutoring with Lead-Tutor",
  "manual_lead": "Practice the Lead-DBS workflow with Lead-Tutor."
}
---

With the publication of Lead Tutor, we came up with a package that is ideal for self-tutoring Lead-DBS based electrode localizations, which includes

* A [scientific paper](https://apertureneuro.org/article/129658-lead-tutor-an-open-access-educational-resource-for-deep-brain-stimulation-electrode-localizations) summarizing the effort
* A [dataset](https://osf.io/jxecg/?view_only=f2765a6aa3604dea8afa14365b70381c) of anonymized imaging data from ten DBS patients
* A tool (integrated into Lead-DBS) that you can used to check your results

Get started by downloading the dataset and paper (links above). Load up the dataset in Lead-DBS and start localizing.

![After loading the downloaded Lead Tutor dataset to Lead-DBS, a button to "Submit Results..." appears in the top right.](manual/7e57b49f211c9da6.png "After loading the downloaded Lead Tutor dataset to Lead-DBS, a button to &quot;Submit Results...&quot; appears in the top right.")

After loading the downloaded Lead Tutor dataset to Lead-DBS, a button to "Submit Results..." appears in the top right. Once you are happy with your localizations, you can submit results to have Lead Tutor automatically compare them with ground truth expert localizations made on the same subjects.

![Lead Tutor result: This page, shown once clicking "Submit results..." will give you feedback on how accurate the results were.](manual/174dfb091eb32c37.png "Lead Tutor result: This page, shown once clicking &quot;Submit results...&quot; will give you feedback on how accurate the results were.")

The resulting page, shown once clicking "Submit results..." will give you feedback on how accurate the results were. You can repeat the process as often as you would like, either by starting from scratch or by refining your localizations.

{{% manual-note "info" %}}
For SEEG electrode reconstructions with LEGUI, you may download publicly available datasets to use as training datasets. An example on OpenNeuro is the[ Numbers dataset](https://openneuro.org/datasets/ds005415/versions/1.0.0) (Rockhill et al.).
{{% /manual-note %}}
