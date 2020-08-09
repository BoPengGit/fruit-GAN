import tensorflow as tf  


def train(dataset, epochs):
  train_iterator = iter(dataset)
  for epoch in range(epochs):
    train_steps(train_iterator, tf.convert_to_tensor(steps_per_epoch))

@tf.function
def train_steps(iterator, steps):
  for _ in tf.range(steps):
    strategy.run(train_step_function, args=(next(iterator),))


def train_step_function(images, augmentation=None):
  noise = tf.random.normal([per_replica_batch_size, noise_dim])

  with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
    generated_images = generator(noise, training=True)
    
    if augmentation:
        real_output = discriminator(DiffAugment(images, policy=augmentation), training=True)
        fake_output = discriminator(DiffAugment(generated_images, policy=augmentation), training=True)
    else:
        real_output = discriminator(images, training=True)
        fake_output = discriminator(generated_images, training=True)

    gen_loss = generator_loss(fake_output)

    disc_loss = discriminator_loss(real_output, fake_output)

  gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
  gradients_of_discriminator = disc_tape.gradient(disc_loss, discriminator.trainable_variables)

  generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
  discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, discriminator.trainable_variables))





