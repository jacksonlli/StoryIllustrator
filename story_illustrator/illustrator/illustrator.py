from stable_diffusion.optimizedSD.optimized_txt2img import main as txt2img


prompt = "emma watson looking at camera, cloudy sky background, ln illustration concept art, lotr, anime key visual, portrait, long flowing hair, fine detail, delicate features, gapmoe kuudere trending pixiv by victo ngai fanbox by greg rutkowski makoto shinkai takashi takeuchi, studio ghibli, 100mm, sharp edges, smooth"
negative_prompt = "duplicate, morbid, mutilated, out of frame, extra fingers, mutated hand, mutation, deformed, blurry, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, extra limbs, bad anatomy, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, mutated hands, fused fingers, too many fingers"
txt2img(
    prompt=prompt,
    negative_prompt=negative_prompt,
    ddim_steps=30,
    n_samples=1,
    outdir="../outputs/"
)