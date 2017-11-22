# ImageWatermark
Huawei's Serverless example, add watermark on image uploaded to OBS by user using serverless function
step in step
1. create a origin burket and a printwater burket in obs.
2. create a Agency in IAM.
3. create a function in FunctionStage.
4. select the agency your created.
5. add configuration in customized configuration printwater burket. for example:obs_output_bucket=water-burket
6. create a obs trigger.
7. upload a picture to origin burket in obs.
8. watch the function in log.
