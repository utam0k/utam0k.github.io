---
title: "Rust's std::default::Default"
date: 2018-05-28T21:56:49+09:00
tags: [tech, rust]
---

Rust’s standard library has [Default](https://doc.rust-lang.org/std/default/trait.Default.html), which lets you define default values for structs. I looked at practical examples and how it’s implemented in `libcore`.

The trait looks like this:

```rust
pub trait Default {
    fn default() -> Self;
}
```

## Examples
1. Without Default  
If you don’t use Default, you typically write `new()` yourself.

    ```rust
    struct SomeOptions {
        foo: i32,
        bar: f32,
    }

    impl SomeOptions {
        fn new() -> Self {
            Self { foo: 0, bar: 0.0f32 }
        }
    }

    fn main() {
        let options: SomeOptions = SomeOptions::new();
    }
    ```

2. Using Default  
The [docs](https://doc.rust-lang.org/std/default/trait.Default.html) show this. Deriving `Default` lets `Default::default()` replace `SomeOptions::new()`, so you don’t need to write `new()`—nice and convenient.

    ```rust
    #[derive(Default)]
    struct SomeOptions {
        foo: i32,
        bar: f32,
    }

    fn main() {
        let options: SomeOptions = Default::default();
    }
    ```

3. Overriding just part of the defaults  
Also from the docs: you can override only some fields.

    ```rust
    fn main() {
        let options = SomeOptions { foo: 42, ..Default::default() };
    }
    ```

4. Implementing Default yourself  
Of course you can implement the trait manually. The docs show an enum example; here’s a struct.

    ```rust
    struct SomeOptions {
        foo: i32,
        bar: f32,
    }

    impl Default for SomeOptions {
        fn default() -> Self {
            Self { foo: 0, bar: 0.0f32 }
        }
    }

    fn main() {
        let options: SomeOptions = Default::default();
    }
    ```

5. unwrap_or_default()  
`Result` and `Option` implement [unwrap_or_default()](https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or_default). Example with Option:

    ```rust
    #[derive(Default, Debug, PartialEq)]
    struct SomeOptions {
        foo: i32,
        bar: f32,
    }

    fn main() {
        let options: SomeOptions = None.unwrap_or_default();
        assert_eq!(options, Default::default());
    }
    ```

6. Real-world use  
[glium](https://github.com/glium/glium), an OpenGL wrapper, has a large struct called [DrawParameters](https://github.com/glium/glium/blob/v0.13.5/src/draw_parameters/mod.rs#L246-L381):

    ```rust
    pub struct DrawParameters<'a> {
        pub depth: Depth,
        pub stencil: Stencil,
        pub blend: Blend,
        pub color_mask: (bool, bool, bool, bool),
        pub line_width: Option<f32>,
        pub point_size: Option<f32>,
        pub clip_planes_bitmask: u32,
        pub backface_culling: BackfaceCullingMode,
        pub polygon_mode: PolygonMode,
        pub multisampling: bool,
        pub dithering: bool,
        pub viewport: Option<Rect>,
        pub scissor: Option<Rect>,
        pub draw_primitives: bool,
        pub samples_passed_query: Option<SamplesQueryParam<'a>>,
        pub time_elapsed_query: Option<&'a TimeElapsedQuery>,
        pub primitives_generated_query: Option<&'a PrimitivesGeneratedQuery>,
        pub transform_feedback_primitives_written_query:
            Option<&'a TransformFeedbackPrimitivesWrittenQuery>,
        pub condition: Option<ConditionalRendering<'a>>,
        pub transform_feedback: Option<&'a TransformFeedbackSession<'a>>,
        pub smooth: Option<Smooth>,
        pub provoking_vertex: ProvokingVertex,
        pub primitive_bounding_box: (Range<f32>, Range<f32>, Range<f32>, Range<f32>),
        pub primitive_restart_index: bool,
    }
    ```

    Writing all of that each time would be painful, so Default is [implemented](https://github.com/glium/glium/blob/v0.13.5/src/draw_parameters/mod.rs#L421-L448). With it, you only set fields you want to change from the defaults.

    ```rust
    let params = glium::DrawParameters {
        point_size: Some(5.0),
        multisampling: false,
        ..Default::default()
        };
    ```

## Details
Some types in the core library have fixed defaults. As of 1.26 they are:

type  | default
-------- | -----
bool | false
char | '\x00'
usize | 0
u8 | 0
u16 | 0
u32 | 0
u64 | 0
u128 | 0
isize | 0
i8 | 0
i16 | 0
i32 | 0
i64 | 0
i128 | 0
f32 | 0
f64 | 0

### Implementation in libcore
In 1.26, Default is implemented with a macro called `default_impl!`. Looking at the [code](https://github.com/rust-lang/rust/blob/1.26.0/src/libcore/default.rs#L128-L158), you’ll see the cases that correspond to the table above.

```rust
macro_rules! default_impl {
    ($t:ty, $v:expr, $doc:tt) => {
        #[stable(feature = "rust1", since = "1.0.0")]
        impl Default for $t {
            #[inline]
            #[doc = $doc]
            fn default() -> $t { $v }
        }
    }
}

default_impl! { bool, false, "Returns the default value of `false`" }
```

There are also implementations for tuples and [many more](https://doc.rust-lang.org/std/default/trait.Default.html#implementors).

## Addendum (2018-05-29)
[lo48576](https://mastodon.cardina1.red/@lo48576) told me a couple of extra points, so I’m adding them.

### 1
`std::default::Default` is imported automatically via the [prelude](https://github.com/rust-lang/rust/blob/1.26.0/src/libcore/prelude/v1.rs#L44). You can call `SomeOptions::default()` instead of `Default::default()`.

*Improved Example 1*
```rust
#[derive(Default)]
struct SomeOptions {
    foo: i32,
    bar: f32,
}

fn main() {
    let options = SomeOptions::default();
}
```

### 2
The following code using `#[derive(Default)]` won’t compile. Because `Option`’s default is `None`, `NoDefault` itself doesn’t need to implement Default. To make it compile, implement Default manually.

*NG:*
```rust
// Struct with no default impl.
struct NoDefault;

#[derive(Default)]
struct SomeOptions<Content> {
    foo: Option<Content>,
    bar: f32,
}

fn main() {
    // ERROR!
    // error[E0599]: no function or associated 
    // item named `default` found for type 
    // `SomeOptions<NoDefault>` in the 
    // current scope
    let _ = SomeOptions::<NoDefault>::default(); // NG
}
```
*OK:*
```rust
// Struct with no default impl.
struct NoDefault;

struct SomeOptions<Content> {
    foo: Option<Content>,
    bar: f32,
}

impl<Content> Default for SomeOptions<Content> {
    fn default() -> Self {
        Self {
            foo: Default::default(),
            bar: Default::default(),
        }
    }
}

fn main() {
    let _ = SomeOptions::<NoDefault>::default(); // OK
}
```
