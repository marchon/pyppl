# Caching
<!-- toc -->

Once a job is cached, `pyppl` will skip running this job. But you have to tell a process how to cache its jobs by setting `p.cache` with a valid caching method:

|Caching method (`p.cache=?`)|How|
|-|-|
|`True`|A signature<sup>*</sup> of input files, script and output files of a job is cached in `<workdir>/cached.jobs`, compare the signature before a job is running.|
|`False`| Disable caching, always run jobs.|
|`"export"`| First try to find the signatures, if failed, try to restore the files existed (or exported before in `p.exdir`).

  
> **Hint**: `p.cache = "export"` is extremely useful for a process that you only want it to run successfully once, export the result files and never run the process again. You can even delete the `<workdir>` of the process, but `pyppl` will find the exported files and use them as the input for its next processes. So you don't need to modify the pipeline.  
One scenario is that you can use it to download some files and never need to download them again.
