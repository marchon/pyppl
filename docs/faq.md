# FAQ

**Q: Do I have to use the variable name as the process id?**

A: No, you can use a different one by `pWhatever = proc (id=pYourId)`, or `pWhatever = proc ()`, and then change the id by `pWhatever.id = 'pYourId'`

**Q: When should I use `p.brings`?**

A: In most cases, index files. You don't want those files to be involved in the caching.

**Q: What's the difference between `input` and `args`?**

A: Basically, `args` are supposed to be arguments shared among all jobs in the process. Files in `args` are not linked in the `job.indir` folder.

**Q: Does a `proc` remain the same after it's used to construct an `aggr`?**

A: No, it will be a copy of the original one. So the original be used somewhere else.
