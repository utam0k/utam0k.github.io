---
title: "Rustのstd::default::Default"
date: 2018-05-28T21:56:49+09:00
tags : [tech, rust]
---

Rustのstdに[Default](https://doc.rust-lang.org/std/default/trait.Default.html)というのがある。  
構造体のデフォルト値を決めることができる。  
実用例からlibcoreでのどのような実装になっているかを見てみた。  

traitはこんな感じ。

```rust
pub trait Default {
    fn default() -> Self;
}
```

# Example
1. Defaultなし  
Defaultを利用しないとこんな感じで`new()`を作るようになる。

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

2. Defaultを使う    
以下は[ドキュメント](https://doc.rust-lang.org/std/default/trait.Default.html)のコードです。   
`#[derive]`[アトリビュート](http://rust-lang-ja.org/rust-by-example/attribute.html)で[Default](https://doc.rust-lang.org/std/default/trait.Default.html)を使うことで`Default::default()`が`SomeOptions::new()`の代わりになって`new()`を定義する必要がなくなりました！はい、便利。

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

3. 一部の値だけデフォルトを用いる  
以下は[ドキュメント](https://doc.rust-lang.org/std/default/trait.Default.html)のコードです。  
一部の値だけデフォルトの値を使うともできる

    ```rust
    fn main() {
        let options = SomeOptions { foo: 42, ..Default::default() };
    }
    ```

4. Defaultを実装する  
Defaultトレイトを自分で実装することももちろん可能。  
ドキュメントではEnumを用いた[コード](https://doc.rust-lang.org/std/default/trait.Default.html#how-can-i-implement-default)を紹介していた。

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
`Result`や`Option`では[unwrap_or_default()](https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or_default)という関数が実装されている。  
Optionを用いた例

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

6. 実用例  
[glium](https://github.com/glium/glium)というOpenGLのラッパーでは[DrawParameters](https://github.com/glium/glium/blob/v0.13.5/src/draw_parameters/mod.rs#L246-L381)というでかい構造体がある。

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

    さすがにこれを毎回書くのはしんどいのでDefaultトレイトが[実装](https://github.com/glium/glium/blob/v0.13.5/src/draw_parameters/mod.rs#L421-L448)されている。
    Defaultトレイトを実装することでDefaultから変更したい箇所だけ書けばよくなる。  

    ```rust
    let params = glium::DrawParameters {
        point_size: Some(5.0),
        multisampling: false,
        ..Default::default()
        };
    ```

# 詳細
Rustのcoreライブラリではデフォルト値が決まっているものがある。
1.26時点では以下のようになっている。

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

### libcoreの実装
1.26のDefaultのは`default_imp!`というマクロを用いて実装されている。  
実際の[実装コード](https://github.com/rust-lang/rust/blob/1.26.0/src/libcore/default.rs#L128-L158)を見てもらうとがさっきの表の箇所が実装されているのがわかる。

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

これ以外にも`tuple`でも[実装](https://github.com/rust-lang/rust/blob/1.26.0/src/libcore/tuple.rs#L73-L78)されていた。  
他にも[いっぱい](https://doc.rust-lang.org/std/default/trait.Default.html#implementors)あるみたいです。

## 追記(2018-05-29)
[lo48576さん](https://mastodon.cardina1.red/@lo48576)さんにこんなこともできるよと教えていただいたので追記。  

### その1  
`std::default::Default`は[prelude経由](https://github.com/rust-lang/rust/blob/1.26.0/src/libcore/prelude/v1.rs#L44)で自動的にインポートされています。
`Default::default()`の代わりに`SomeOptions::default()`でできます。  

*Example1の改良*
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

### その2  
`#[derive(Default)]`を用いた以下のようなコードはコンパイルが通りません。 

`Option`のデフォルトは`None`なので`NoDefault構造体`は`Default`を実装する必要がありません。  
コンパイルを通するには`Default`を実装します。  

{{< columns >}}
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
{{< column >}}
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
{{< endcolumns >}}

[qnighyさんの記事](http://qnighy.hatenablog.com/entry/2017/06/01/070000)や[lo48576さんの記事](https://blog.cardina1.red/2016/03/24/rust-default-wont-compile/)
の記事が参考になると思います。 
